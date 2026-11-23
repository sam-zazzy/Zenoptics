"""Builds the 2026 blog posts from the "Blog Content Archive" folder (Word documents), then rebuilds the blog listing.
Run from the repo root (needs python-docx, openpyxl and Pillow):

    python3 tools/build-blog-archive.py && python3 tools/build-pages.py && python3 tools/seo.py && npm run build

What it does
- Reads "_STATUS - All published blogs, documents, images and links.xlsx" for each post's slug, date and title.
- For every published post with a document, writes blog/<slug>/index.html (same template as the moved posts).
  Documents flagged NOT PUBLISHED, CANCELLED, UNCONFIRMED or ZAZZY DRAFT are skipped; where a PUBLISHED TEXT version
  exists it is used.
- Cover: the banner inside the document when there is one (or a file in COVERS below); otherwise a branded
  title cover is rendered (assets/images/blog/<slug>/cover.webp, marked in GENERATED_COVERS.txt) until the real
  banner is supplied.
- Rebuilds blog/index.html: latest post on top, then every post newest first. Refreshes "More from the blog" on every post.
"""
import os, re, sys, json, html, glob, datetime, subprocess, collections
import docx, openpyxl
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.text.hyperlink import Hyperlink
from PIL import Image

ARCHIVE = "Blog Content Archive"
SITE = "https://zenoptics.com"
esc = lambda s: html.escape(s or "", quote=True)
nice_date = lambda d: datetime.date.fromisoformat(d).strftime("%B %-d, %Y")
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower().replace("’", "'")).strip()

# Extra images that are not inside the documents (Blog Images folder)
COVERS = {"kpi-rollout-plan-business-teams": f"{ARCHIVE}/Blog Images/Blog_021126_Center.png"}
INLINE = {"kpi-rollout-plan-business-teams": (f"{ARCHIVE}/Blog Images/Blog_021126_In-between.png", "Decide how historical comparisons will work",
                                              "Previous and updated KPI definitions bridged by an effective date for historical comparison")}

# ---------------- status sheet ----------------
wb = openpyxl.load_workbook(f"{ARCHIVE}/_STATUS - All published blogs, documents, images and links.xlsx")
status = {}
for r in list(wb.active.iter_rows(values_only=True))[1:]:
    if r[1]: status[r[1]] = {"date": r[0].date().isoformat(), "title": r[2], "era": r[3]}

# ---------------- pick one document per published slug ----------------
SKIP = re.compile(r"NOT PUBLISHED|NOT YET PUBLISHED|CANCELLED|UNCONFIRMED|ZAZZY DRAFT", re.I)
docs = collections.defaultdict(list)
for f in sorted(glob.glob(f"{ARCHIVE}/*.docx")):
    name = os.path.basename(f)
    if name.startswith("_") or " - " not in name or SKIP.search(name): continue
    docs[name.split(" - ")[0]].append(f)
chosen = {}
for slug, fs in docs.items():
    if slug not in status: continue
    fs.sort(key=lambda f: "PUBLISHED TEXT" not in f)
    chosen[slug] = fs[0]

existing = {d for d in os.listdir("blog") if os.path.isfile(f"blog/{d}/index.html")}
published = set(chosen) | existing
REPO_DIRS = {d for d in os.listdir(".") if os.path.isfile(os.path.join(d, "index.html"))}

# ---------------- docx helpers ----------------
LABELS = {"zenoptics blog publication package", "seo and publishing instructions", "social media post", "seo publishing details",
          "source and internal link references", "linkedin post copy", "seo and aeo publishing metadata"}
META_LINE = re.compile(r"^(role|primary[ _]keywords?|audience|seo[ _]title|meta[ _]description|proposed[ _]slug|distinct[ _]angle|website[ _]copy|"
                       r"related[ _]searches|secondary[ _]keywords?|url[ _]slug|slug|url|title|subtitle|hub|internal[ _]links?|status|cluster)\s*[:|]", re.I)
CTA_START = re.compile(r"^(schedule|request|talk to|ready to|book|see how|explore|discover|bring|see the|see what)", re.I)
removed_links = collections.Counter()
RENAMED = {"build-vs-buy-analytics-portal": "analytics-portal-governance-layer", "ai-decisions-explainable": "beyond-explainable-ai-decision-accountability"}

def fix_href(href):
    m = re.match(r"https?://(?:www\.)?zenoptics\.com(/[^#?]*)?([?#].*)?$", href or "")
    if "calendly.com" in (href or ""): return "../../schedule-a-demo/"
    if not m: return href
    parts = [p for p in (m.group(1) or "/").split("/") if p]
    rest = m.group(2) or ""
    if not parts: return "../../" + rest
    if parts[0] in ("request-demo", "demo", "schedule-a-demo", "contact"): return "../../schedule-a-demo/"
    if parts[0] == "blog" and len(parts) == 2:
        parts[1] = RENAMED.get(parts[1], parts[1])
        return f"../{parts[1]}/{rest}" if parts[1] in published else None
    if len(parts) == 1 and parts[0] in REPO_DIRS: return f"../../{parts[0]}/{rest}"
    return None

def inline_html(p):
    out = []
    for item in p.iter_inner_content():
        if isinstance(item, Hyperlink):
            text = esc("".join(r.text for r in item.runs))
            href = fix_href(item.address) if item.address else None
            if href:
                ext = "" if href.startswith("../") else ' target="_blank" rel="noopener"'
                out.append(f'<a href="{esc(href)}"{ext}>{text}</a>')
            else:
                removed_links[item.address or "(anchor)"] += 1; out.append(text)
        else:
            t = esc(item.text).replace("\n", " ")
            if not t: continue
            if item.bold: t = f"<strong>{t}</strong>"
            if item.italic: t = f"<em>{t}</em>"
            out.append(t)
    s = "".join(out)
    s = re.sub(r"\s*\[(?:Verify|Note|TODO|Check|Confirm|Editor|Source needed)\b[^\]]*\]", "", s, flags=re.I)  # editorial notes
    s = re.sub(r"</strong><strong>", "", s); s = re.sub(r"</em><em>", "", s)
    return s.strip()

def list_kind(d, p):
    pPr = p._p.pPr
    if pPr is None or pPr.numPr is None or pPr.numPr.numId is None: return None
    try:
        num_id = pPr.numPr.numId.val; ilvl = pPr.numPr.ilvl.val if pPr.numPr.ilvl is not None else 0
        numbering = d.part.numbering_part.element
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        abs_id = numbering.xpath(f'w:num[@w:numId="{num_id}"]/w:abstractNumId/@w:val', namespaces=ns)[0]
        fmt = numbering.xpath(f'w:abstractNum[@w:abstractNumId="{abs_id}"]/w:lvl[@w:ilvl="{ilvl}"]/w:numFmt/@w:val', namespaces=ns)
        return "ol" if fmt and fmt[0] not in ("bullet", "none") else "ul"
    except Exception:
        return "ul"

def blocks(d):
    for el in d.element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p": yield Paragraph(el, d)
        elif tag == "tbl": yield Table(el, d)

def table_html(t):
    rows = [[esc(c.text.strip()).replace("\n", "<br>") for c in r.cells] for r in t.rows]
    if not rows: return ""
    head = "".join(f"<th>{c}</th>" for c in rows[0])
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:])
    return f'<div class="table-wrap"><table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table></div>'

def slugify(t): return re.sub(r"[^a-z0-9]+", "-", html.unescape(re.sub(r"<[^>]+>", "", t)).lower()).strip("-")[:80]

def convert(slug, path):
    d = docx.Document(path)
    allb = list(blocks(d))
    texts = [b.text.strip() for b in allb if isinstance(b, Paragraph)]
    meta_desc = next((re.sub(r'^meta[ _]description\s*:?\s*', "", t, flags=re.I).strip().strip('"“”')
                      for t in texts if re.match(r"meta[ _]description\b", t, re.I) and len(t) > 40), None)
    # article start: first title / heading 1 that is not an editorial label
    start = next(i for i, b in enumerate(allb) if isinstance(b, Paragraph) and b.style.name in ("Title", "Heading 1")
                 and b.text.strip() and norm(b.text) not in LABELS)
    tstyle = allb[start].style.name
    doc_title = allb[start].text.strip()
    end = len(allb)
    for i in range(start + 1, len(allb)):
        b = allb[i]
        if isinstance(b, Paragraph) and b.text.strip() and (
                re.fullmatch(r"(old|previous) version|earlier draft", b.text.strip(), re.I) or b.style.name == tstyle or (b.style.name in ("Title", "Heading 1") and norm(b.text) in LABELS) or b.style.name == "Title"):
            end = i; break
    body = allb[start + 1:end]
    hstyles = sorted({b.style.name for b in body if isinstance(b, Paragraph) and b.style.name.startswith("Heading") and b.text.strip()})
    level = {s: ("h2" if i == 0 else "h3") for i, s in enumerate(hstyles)}
    subtitle = None
    out, faq, in_faq, lst = [], [], False, None
    skip_kw, refs = False, None
    words = 0
    def close_refs():
        nonlocal refs
        if refs: out.append('<div class="refs">\n' + "\n".join(f"<p>{x}</p>" for x in refs) + "\n</div>"); refs = None
    def close_list():
        nonlocal lst
        if lst: out.append(f"<{lst[0]}>\n" + "\n".join(f"<li>{x}</li>" for x in lst[1]) + f"\n</{lst[0]}>"); lst = None
    paras = [b for b in body if isinstance(b, Paragraph) and b.text.strip() and not b.style.name.startswith(("Heading", "Subtitle"))]
    last_para = paras[-1] if paras else None
    for b in body:
        if isinstance(b, Table):
            close_list(); out.append(table_html(b)); continue
        t = b.text.strip(); st = b.style.name
        if not t: continue
        if st == "Subtitle": subtitle = t; continue
        if META_LINE.match(t) or t.startswith(("Published [DATE", "Agency instruction")) or re.fullmatch(r"\[[^\]]*\]", t):
            skip_kw = t.endswith(":"); continue
        if skip_kw and not st.startswith("Heading") and len(t) < 80 and not t.endswith("."): continue
        skip_kw = False
        if st.startswith("Heading"):
            close_list(); close_refs(); tag = level.get(st, "h3"); txt = inline_html(b)
            if tag == "h2":
                in_faq = bool(re.search(r"frequently asked|^faq\b", t, re.I))
                if re.fullmatch(r"references|sources", t, re.I): refs = []
            if in_faq and tag == "h3": faq.append([t, []])
            out.append(f"<{tag}>{re.sub(r'</?strong>', '', txt)}</{tag}>")
            if INLINE.get(slug) and norm(t) == norm(INLINE[slug][1]): out.append("<!--INLINE-IMG-->")
            continue
        h = inline_html(b); words += len(t.split())
        if refs is not None: refs.append(h); continue
        kind = list_kind(d, b)
        if kind:
            if lst and lst[0] != kind: close_list()
            if not lst: lst = (kind, [])
            lst[1].append(h); continue
        close_list()
        if len(re.findall(r"\b(?:Slug|URL|Meta description|Primary keyword|Secondary keywords|Status|Hub|Internal links):", t)) >= 2: continue
        if b is last_para and len(t) < 320 and (CTA_START.match(t) or not t.endswith(".")):
            plain = re.sub(r":?\s*https?://\S+", "", t).strip().rstrip(".")
            out.append(f'<p class="post-cta"><a href="../../schedule-a-demo/">{esc(plain)}</a></p>')
            continue
        if in_faq:
            m = re.match(r"^<strong>(.+?\?)</strong>\s*(.*)$", h)
            if m:
                faq.append([html.unescape(re.sub(r"<[^>]+>", "", m.group(1))), [m.group(2)] if m.group(2) else []])
                out.append(f"<h3>{m.group(1)}</h3>");
                if m.group(2): out.append(f"<p>{m.group(2)}</p>")
                continue
            m = re.match(r"^([^?]{10,200}\?)\s+(\S.*)$", h)
            if m and "<" not in m.group(1):
                faq.append([html.unescape(m.group(1)), [m.group(2)]])
                out.append(f"<h3>{m.group(1)}</h3>"); out.append(f"<p>{m.group(2)}</p>"); continue
            if t.endswith("?") and len(t) < 220:
                faq.append([t, []]); out.append(f"<h3>{re.sub(r'</?strong>', '', h)}</h3>"); continue
            if faq: faq[-1][1].append(h)
        h = re.sub(r"(?:\s*[:\-–]\s*)?https?://calendly\.com/\S+", "", h)
        out.append(f"<p>{h}</p>")
    close_list(); close_refs()
    return {"doc_title": doc_title, "subtitle": subtitle, "meta": meta_desc, "html": out, "faq": faq, "words": words}

def fit_desc(text):
    """Meta description of 110-160 characters: whole sentences when they fit, otherwise cut at a word."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= 160: return text
    out = ""
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if len(out) + len(sent) + 1 > 160: break
        out = (out + " " + sent).strip()
    if len(out) >= 100: return out
    return text[:157].rsplit(" ", 1)[0].rstrip(",;:") + "…"

# ---------------- images ----------------
def save_webp(src, dest, max_w):
    im = Image.open(src).convert("RGB")
    if im.width > max_w: im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(dest, "WEBP", quality=82, method=6); return im.size

def docx_image(path):
    import zipfile
    with zipfile.ZipFile(path) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        if not media: return None
        out = f"/tmp/_cover_{os.getpid()}" + os.path.splitext(media[0])[1]
        open(out, "wb").write(z.read(media[0])); return out

generated = []
def render_title_covers(items):
    """Branded cover (navy, arcs, logo, title) for posts without a banner. Rendered with Chrome via playwright-core."""
    if not items: return
    js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render-covers.js")
    data = json.dumps([{"slug": s, "title": t} for s, t in items])
    open("/tmp/_covers.json", "w").write(data)
    subprocess.run(["node", js, "/tmp/_covers.json", os.getcwd()], check=True)
    for s, _ in items:
        png = f"assets/images/blog/{s}/cover.png"
        save_webp(png, f"assets/images/blog/{s}/cover.webp", 1600); save_webp(png, f"assets/images/blog/{s}/cover-800.webp", 800)
        os.remove(png)

# ---------------- build ----------------
tpl_file = "blog/how-to-control-report-sprawl/index.html"
tpl = open(tpl_file, encoding="utf-8").read()
HEADER = tpl[tpl.index("<body"):tpl.index('<main id="main">')]
FOOTER = tpl[tpl.index("</main>") + len("</main>"):]
PLATFORM = tpl[tpl.index("    <!-- ============ ONE PLATFORM"):tpl.index("    <!-- ============ MORE FROM THE BLOG")]

posts = {}
need_cover = []
for slug, path in sorted(chosen.items()):
    st = status[slug]; c = convert(slug, path)
    title = c["doc_title"] if norm(c["doc_title"]).startswith(norm(st["title"])) else st["title"]
    first_p = next((re.sub(r"<[^>]+>", "", html.unescape(x[3:-4])) for x in c["html"] if x.startswith("<p>")), "")
    desc = fit_desc(c["meta"]) if c["meta"] else None
    if not desc or len(desc) < 100: desc = fit_desc(first_p)
    out = f"assets/images/blog/{slug}"; os.makedirs(out, exist_ok=True)
    src = COVERS.get(slug) or docx_image(path)
    if src:
        size = save_webp(src, f"{out}/cover.webp", 1600); save_webp(src, f"{out}/cover-800.webp", 800)
    else:
        need_cover.append((slug, title)); size = (1600, 900)
    body = "\n".join(c["html"])
    if slug in INLINE:
        isrc, _, alt = INLINE[slug]; w, h = save_webp(isrc, f"{out}/historical-comparison.webp", 1600)
        body = body.replace("<!--INLINE-IMG-->", f'<figure><img src="../../assets/images/blog/{slug}/historical-comparison.webp" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>')
    posts[slug] = dict(slug=slug, date=st["date"], title=title, description=desc, subtitle=c["subtitle"], body=body, faq=c["faq"],
                       mins=max(1, round(c["words"] / 230)), cover=size)

render_title_covers(need_cover)
for slug, _ in need_cover:
    posts[slug]["cover"] = Image.open(f"assets/images/blog/{slug}/cover.webp").size
open(f"{ARCHIVE}/GENERATED_COVERS.txt", "w").write(
    "Posts whose cover was generated (title on a branded background) because the real banner is not in this folder.\n"
    "Put the real banner in Blog Images/, add it to COVERS in tools/build-blog-archive.py and run the build again.\n\n"
    + "\n".join(s for s, _ in need_cover) + "\n")

# ---------------- every post on the site (for the listing and related posts) ----------------
def post_meta(slug):
    s = open(f"blog/{slug}/index.html", encoding="utf-8").read()
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    return dict(slug=slug, date=ld["datePublished"], title=ld["headline"], description=ld["description"])
everything = {s: post_meta(s) for s in existing if s not in posts}
everything.update({s: {k: p[k] for k in ("slug", "date", "title", "description")} for s, p in posts.items()})
ordered = sorted(everything.values(), key=lambda p: (p["date"], p["slug"]), reverse=True)

CARD_LI = "relative flex flex-col overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(30,48,95,0.08)] ring-1 ring-slate-200 transition hover:shadow-[0_12px_36px_rgba(30,48,95,0.16)] has-[a:focus-visible]:ring-2 has-[a:focus-visible]:ring-navy"
def card(p, from_post):
    pre = "../../" if from_post else "../"; link = f"../{p['slug']}/" if from_post else f"{p['slug']}/"
    return f"""          <li class="{CARD_LI}">
            <img src="{pre}assets/images/blog/{p['slug']}/cover-800.webp" alt="" width="800" height="450" loading="lazy" decoding="async" class="aspect-video w-full object-cover">
            <div class="flex flex-1 flex-col p-6">
              <time datetime="{p['date']}" class="text-sm text-navy/70">{nice_date(p['date'])}</time>
              <h3 class="mt-2 text-lg leading-snug font-semibold"><a href="{link}" class="after:absolute after:inset-0 focus-visible:outline-none">{esc(p['title'])}</a></h3>
              <p class="mt-3 line-clamp-3 text-navy/80">{esc(p['description'])}</p>
            </div>
          </li>"""

def related(slug):
    i = next(k for k, p in enumerate(ordered) if p["slug"] == slug)
    near = sorted((p for p in ordered if p["slug"] != slug), key=lambda p: abs(ordered.index(p) - i))[:3]
    return "\n".join(card(p, True) for p in sorted(near, key=lambda p: p["date"], reverse=True))

def headings_with_ids(b):
    seen = set()
    def hid(m):
        lvl, inner = m.group(1), m.group(2); i = slugify(inner) or "section"; base, n = i, 2
        while i in seen: i = f"{base}-{n}"; n += 1
        seen.add(i); return f'<h{lvl} id="{i}">{inner}</h{lvl}>'
    b = re.sub(r"<h([23])>([\s\S]*?)</h\1>", hid, b)
    toc = [(m.group(1), html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()) for m in re.finditer(r'<h2 id="([^"]+)">([\s\S]*?)</h2>', b)]
    return b, toc

for slug, p in posts.items():
    url = f"{SITE}/blog/{slug}/"; body, toc = headings_with_ids(p["body"])
    title = f"{p['title']} | ZenOptics"; cover_abs = f"{SITE}/assets/images/blog/{slug}/cover.webp"; w, h = p["cover"]
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"],
           "description": p["description"], "image": cover_abs, "mainEntityOfPage": url,
           "author": {"@type": "Organization", "name": "ZenOptics"}, "publisher": {"@type": "Organization", "name": "ZenOptics"}}]
    faq = [(q, " ".join(re.sub(r"<[^>]+>", "", html.unescape(a)) for a in ans)) for q, ans in p["faq"]]
    faq = [(q, a) for q, a in faq if a]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage",
                   "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    lds = "\n".join(f'  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    toc_items = "\n".join(f'              <li><a href="#{i}" class="hover:underline">{esc(t)}</a></li>' for i, t in toc)
    aside = f"""      <aside class="lg:order-last" aria-label="On this page">
        <details class="rounded-2xl bg-soft p-5 lg:hidden">
          <summary class="font-semibold">On this page</summary>
          <ol class="mt-4 list-decimal space-y-2 pl-5 text-sm">
{toc_items}
          </ol>
        </details>
        <div class="sticky top-28 hidden rounded-2xl bg-soft p-6 lg:block">
          <p class="font-semibold">On this page</p>
          <ol class="mt-4 list-decimal space-y-3 pl-5 text-sm leading-snug">
{toc_items}
          </ol>
        </div>
      </aside>
""" if len(toc) >= 2 else ""
    dek = f'\n        <p class="mt-4 max-w-3xl text-lg text-white/90">{esc(p["subtitle"])}</p>' if p["subtitle"] else ""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(p['description'])}">
  <meta name="robots" content="noindex">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="ZenOptics">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(p['description'])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{cover_abs}">
  <meta property="article:published_time" content="{p['date']}">
  <link rel="icon" href="../../assets/images/favicon.ico" sizes="any">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../style.css">
{lds}
</head>
{HEADER}<main id="main">

    <!-- ============ POST HEADER ============ -->
    <!-- Built from the Blog Content Archive (Word document) by tools/build-blog-archive.py -->
    <section class="relative overflow-hidden bg-navy text-white">
      <img src="../../assets/images/imgi_52_circle.svg" alt="" aria-hidden="true" class="pointer-events-none absolute -top-24 -left-24 size-64">
      <img src="../../assets/images/imgi_52_circle.svg" alt="" aria-hidden="true" class="pointer-events-none absolute -right-28 -bottom-24 size-80">
      <div class="container-x relative py-12 sm:py-16">
        <nav aria-label="Breadcrumb"><a href="../" class="text-sm font-medium text-white/85 underline-offset-4 hover:underline">Blog</a></nav>
        <h1 class="mt-4 max-w-4xl text-3xl leading-tight font-semibold [text-shadow:0_5px_19px_#1f7bc0] sm:text-[42px]">{esc(p['title'])}</h1>{dek}
        <p class="mt-5 flex flex-wrap gap-x-6 gap-y-1 text-white/85">
          <span>Published <time datetime="{p['date']}">{nice_date(p['date'])}</time></span>
          <span>{p['mins']} min read</span>
        </p>
      </div>
    </section>

    <!-- ============ COVER IMAGE ============ -->
    <div class="container-x pt-10">
      <img src="../../assets/images/blog/{slug}/cover.webp" alt="" width="{w}" height="{h}" fetchpriority="high" decoding="async" class="mx-auto h-auto w-full max-w-4xl rounded-2xl">
    </div>

    <!-- ============ ARTICLE ============ -->
    <div class="container-x grid grid-cols-1 gap-10 py-12 {'lg:grid-cols-[minmax(0,1fr)_17rem] lg:gap-16 ' if aside else ''}lg:py-16">
{aside}      <article class="prose-zo max-w-[46rem]{'' if aside else ' mx-auto w-full'}">
{body}
      </article>
    </div>

{PLATFORM}    <!-- ============ MORE FROM THE BLOG ============ -->
    <section class="container-x py-16 lg:py-20">
      <div class="flex flex-wrap items-baseline justify-between gap-3">
        <h2 class="text-2xl font-semibold sm:text-3xl">More from the blog</h2>
        <a href="../" class="font-medium underline decoration-brand-orange decoration-2 underline-offset-4 hover:decoration-navy">View all posts</a>
      </div>
      <ul class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
<!--RELATED-->
      </ul>
    </section>

  </main>{FOOTER}"""
    os.makedirs(f"blog/{slug}", exist_ok=True)
    open(f"blog/{slug}/index.html", "w", encoding="utf-8").write(page)

# "More from the blog" on every post: the three posts nearest in date
for p in ordered:
    f = f"blog/{p['slug']}/index.html"; s = open(f, encoding="utf-8").read()
    a = s.index('<ul class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">', s.index("MORE FROM THE BLOG")) + len('<ul class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">')
    b = s.index("      </ul>", a)
    s = s[:a] + "\n" + related(p["slug"]) + "\n" + s[b:]
    open(f, "w", encoding="utf-8").write(s)

# ---------------- listing ----------------
lst = open("blog/index.html", encoding="utf-8").read()
top = ordered[0]
latest = f"""    <!-- ============ LATEST POST ============ -->
    <section class="container-x pt-12 lg:pt-16" aria-label="Latest post">
      <article class="{CARD_LI.replace('flex flex-col', 'grid')} lg:grid-cols-[1.25fr_1fr]">
        <img src="../assets/images/blog/{top['slug']}/cover.webp" alt="" width="1200" height="675" fetchpriority="high" decoding="async" class="aspect-video size-full object-cover lg:aspect-auto">
        <div class="flex flex-col justify-center p-7 sm:p-10">
          <time datetime="{top['date']}" class="text-sm text-navy/70">{nice_date(top['date'])}</time>
          <h2 class="mt-3 text-2xl leading-tight font-semibold sm:text-3xl"><a href="{top['slug']}/" class="after:absolute after:inset-0 focus-visible:outline-none">{esc(top['title'])}</a></h2>
          <p class="mt-4 text-navy/80">{esc(top['description'])}</p>
          <p class="mt-6 font-medium underline decoration-brand-orange decoration-2 underline-offset-4" aria-hidden="true">Read the article</p>
        </div>
      </article>
    </section>

"""
a = lst.index("    <!-- ============ LATEST POST ============ -->"); b = lst.index("    <!-- ============ ALL POSTS")
lst = lst[:a] + latest + lst[b:]
ul = '<ul class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3" data-post-list data-batch="12">'
a = lst.index(ul) + len(ul); b = lst.index("      </ul>", a)
lst = lst[:a] + "\n          <!-- Generated by tools/build-blog-archive.py: every post, newest first (the latest is shown above) -->\n" + "\n".join(card(p, False) for p in ordered[1:]) + "\n" + lst[b:]
open("blog/index.html", "w", encoding="utf-8").write(lst)

print(f"built {len(posts)} posts from documents; {len(need_cover)} with a generated cover; listing has {len(ordered)} posts")
print("links removed (target not on the site):", sum(removed_links.values()))
for k, n in removed_links.most_common(): print(f"  {n:3d}  {k}")
