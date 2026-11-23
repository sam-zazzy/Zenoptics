#!/usr/bin/env python3
"""SEO / AEO / GEO upkeep for zenoptics.com. Run from the repo root before every push to main:

    python3 tools/seo.py

It does three things:
  1. Sets the title, meta description, canonical, Open Graph and Twitter tags of the pages listed in PAGES.
  2. Writes sitemap.xml (every indexable page), robots.txt and llms.txt.
  3. Prints an audit of every page: missing or badly sized titles/descriptions, h1 count, canonical, og tags, images without alt.

Pages with <meta name="robots" content="noindex..."> stay out of the sitemap and llms.txt.
Blog posts keep the tags that blog/<slug>/index.html already has.
"""
import datetime, glob, html, os, re, subprocess

SITE = "https://zenoptics.com"
OG_IMAGE = SITE + "/assets/images/og-zenoptics.jpg"   # 1200x630 default share image

# Title ~50-60 characters, description ~140-160 characters. Written from each page's own content.
PAGES = {
    "index.html": dict(
        title="ZenOptics | The Decision Intelligence Platform",
        description="ZenOptics is the decision intelligence platform for enterprise analytics: catalog and govern BI assets with Atlas, add AI context with Nexus, act with Maestro."),
    "atlas/index.html": dict(
        title="Atlas | Analytics System of Record | ZenOptics",
        description="Atlas brings reports, dashboards and KPIs from every BI tool into one governed catalog, so teams find trusted analytics and manage certification and ownership."),
    "nexus/index.html": dict(
        title="Nexus | Analytics Context Layer for AI | ZenOptics",
        description="Nexus gives AI copilots and agents the business context behind your reports and KPIs, turning governed BI metadata and KPI definitions into a context layer."),
    "maestro/index.html": dict(
        title="Maestro | Govern Analytics-Driven Decisions | ZenOptics",
        description="Maestro connects trusted analytics to business workflows. Define what people and AI agents do, require reviews and approvals, and keep a record of decisions."),
    "build-vs-buy-guide/index.html": dict(
        title="Build vs Buy a BI Portal: Executive Guide | ZenOptics",
        description="Is your homegrown BI portal really free? This executive guide gives a build-vs-buy framework for KPI governance, dashboard certification and AI readiness."),
    "schedule-a-demo/index.html": dict(
        title="Schedule a Demo - Unify Analytics with ZenOptics",
        description="Schedule a demo to see how ZenOptics unifies reports, dashboards, and analytics in a single portal, enhancing efficiency, governance, and data accessibility."),
    "resources/index.html": dict(
        title="Thought Leadership and Resource Library | ZenOptics",
        description="Guides, webinars and white papers for analytics leaders who want more efficiency, productivity and value from their BI and analytics investments."),
    "privacy-policy/index.html": dict(
        title="Privacy Policy | ZenOptics",
        description="How ZenOptics collects, uses, shares and protects personal information from our website, events and gated content, and the choices and rights you have."),
    "blog/index.html": dict(
        title="ZenOptics Blog: Analytics Governance, Catalogs and AI",
        description="Insights from the ZenOptics team on analytics governance, analytics catalogs, BI portals, AI context for enterprise analytics and governed decision workflows."),
    "bi-estate-assessment/index.html": dict(
        title="BI Rationalization & BI Estate Assessment | ZenOptics",
        description="Identify reports to retain, consolidate or retire. Explore reporting maintenance costs and discuss a focused BI Estate Assessment with ZenOptics."),
    "trusted-ai/index.html": dict(
        title="Trusted AI for Enterprise Analytics | ZenOptics",
        description="Help AI copilots and agents use the right KPI definitions, owners and governed analytics sources. Discuss a ZenOptics AI Context Workshop."),
}

ORG_LD = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "Organization", "@id": SITE + "/#org", "name": "ZenOptics", "legalName": "Zenoptics Inc.", "url": SITE + "/",
         "logo": SITE + "/assets/images/logo.svg", "email": "info@zenoptics.com",
         "description": "ZenOptics is the decision intelligence platform for enterprise analytics.",
         "address": {"@type": "PostalAddress", "streetAddress": "1762 Technology Drive, Suite 108", "addressLocality": "San Jose",
                     "addressRegion": "CA", "postalCode": "95110", "addressCountry": "US"},
         "sameAs": ["https://twitter.com/ZENOPTICS", "https://www.linkedin.com/company/zenoptics/", "https://www.youtube.com/@zenoptics"]},
        {"@type": "WebSite", "@id": SITE + "/#website", "name": "ZenOptics", "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}},
    ],
}

# llms.txt: the indexable pages in a sensible reading order, with one plain line each
LLMS_ORDER = ["index.html", "atlas/index.html", "nexus/index.html", "maestro/index.html",
              "build-vs-buy-guide/index.html", "resources/index.html", "schedule-a-demo/index.html", "privacy-policy/index.html"]

AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
               "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot"]


def esc(s): return html.escape(s, quote=True)
def url_of(f):
    p = f[:-len("index.html")] if f.endswith("index.html") else f
    return SITE + "/" + p
def read(f): return open(f, encoding="utf-8").read()
def is_noindex(s): return bool(re.search(r'<meta name="robots" content="[^"]*noindex', s))


def set_head(f, cfg):
    s = read(f)
    head_end = s.index("</head>")
    head, rest = s[:head_end], s[head_end:]
    # drop the tags this script owns, then add them back in one block after the viewport meta
    head = re.sub(r'\s*<title>[\s\S]*?</title>', "", head)
    head = re.sub(r'\s*<meta name="description"[^>]*>', "", head)
    head = re.sub(r'\s*<link rel="canonical"[^>]*>', "", head)
    head = re.sub(r'\s*<meta (?:property|name)="(?:og:[a-z:_]+|twitter:[a-z]+)"[^>]*>', "", head)
    head = re.sub(r'\s*<!-- SEO \(tools/seo.py\) -->', "", head)
    head = re.sub(r'\s*<script type="application/ld\+json" data-seo="org">[\s\S]*?</script>', "", head)
    url = url_of(f)
    t, d = esc(cfg["title"]), esc(cfg["description"])
    block = f"""
  <!-- SEO (tools/seo.py) -->
  <title>{t}</title>
  <meta name="description" content="{d}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="ZenOptics">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">"""
    if f == "index.html":
        import json
        block += '\n  <script type="application/ld+json" data-seo="org">' + json.dumps(ORG_LD, ensure_ascii=False) + "</script>"
    m = re.search(r'<meta name="viewport"[^>]*>', head)
    head = head[:m.end()] + block + head[m.end():]
    open(f, "w", encoding="utf-8").write(head + rest)


def all_pages():
    files = sorted(glob.glob("*.html") + glob.glob("*/index.html") + glob.glob("blog/*/index.html"))
    return [f for f in files if not f.startswith(("node_modules/", "tools/"))]


def lastmod(f):
    dirty = subprocess.run(["git", "status", "--porcelain", "--", f], capture_output=True, text=True).stdout.strip()
    if not dirty:
        d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f], capture_output=True, text=True).stdout.strip()
        if d: return d
    return datetime.date.today().isoformat()


def indexable(files):
    out = []
    for f in files:
        if f in ("404.html",): continue
        s = read(f)
        if is_noindex(s) or 'http-equiv="refresh"' in s: continue
        out.append(f)
    return out


def write_sitemap(pages):
    rows = []
    for f in pages:
        pr = "1.0" if f == "index.html" else "0.8" if f.count("/") == 1 else "0.6"
        rows.append(f"  <url>\n    <loc>{url_of(f)}</loc>\n    <lastmod>{lastmod(f)}</lastmod>\n    <priority>{pr}</priority>\n  </url>")
    open("sitemap.xml", "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")


def write_robots():
    ai = "\n".join(f"User-agent: {a}" for a in AI_CRAWLERS)
    open("robots.txt", "w", encoding="utf-8").write(f"""# robots.txt for {SITE}
# Search engines and AI assistants may crawl the whole site.
# Pages that should not be indexed carry <meta name="robots" content="noindex"> instead of a Disallow rule,
# so crawlers can still read that instruction.

User-agent: *
Allow: /

# AI search and assistant crawlers (GEO): allowed, listed explicitly
{ai}
Allow: /

Sitemap: {SITE}/sitemap.xml
""")


def meta(s, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % name, s)
    return html.unescape(m.group(1)) if m else ""


def write_llms(pages):
    def line(f):
        s = read(f)
        t = html.unescape(re.search(r"<title>([\s\S]*?)</title>", s).group(1)).replace(" | ZenOptics", "").strip()
        return f"- [{t}]({url_of(f)}): {meta(s, 'description')}"
    ordered = [f for f in LLMS_ORDER if f in pages] + [f for f in pages if f not in LLMS_ORDER]
    products = [f for f in ordered if f in ("atlas/index.html", "nexus/index.html", "maestro/index.html")]
    rest = [f for f in ordered if f not in products and f != "index.html"]
    open("llms.txt", "w", encoding="utf-8").write(f"""# ZenOptics

> ZenOptics is the decision intelligence platform for enterprise analytics. It brings reports, dashboards and KPIs from many BI tools into one governed catalog (Atlas), gives AI copilots and agents the business context behind that analytics (Nexus), and runs governed, auditable business workflows on top of it (Maestro).

ZenOptics, Inc. is based in San Jose, California. Contact: info@zenoptics.com. Request a demo: {SITE}/schedule-a-demo/

## Products

{chr(10).join(line(f) for f in products)}

## Guides and resources

{chr(10).join(line(f) for f in rest)}

## Home

{line("index.html")}
""")


def audit(files):
    problems = 0
    for f in files:
        s = read(f); noindex = is_noindex(s); flags = []
        t = re.search(r"<title>([\s\S]*?)</title>", s)
        d = meta(s, "description")
        tl = len(html.unescape(t.group(1)).strip()) if t else 0
        if not t: flags.append("no title")
        elif not noindex and not (25 <= tl <= 65): flags.append(f"title {tl} chars")
        if not d: flags.append("no description")
        elif not noindex and not (110 <= len(d) <= 165): flags.append(f"description {len(d)} chars")
        redirect = 'http-equiv="refresh"' in s or 'location.replace(' in s
        if redirect: continue
        if f != "404.html":
            n = len(re.findall(r"<h1\b", s))
            if n != 1: flags.append(f"{n} h1")
            if not noindex:
                if '<link rel="canonical"' not in s: flags.append("no canonical")
                if 'og:title' not in s or 'og:image' not in s: flags.append("og tags missing")
        noalt = len(re.findall(r"<img(?![^>]*\balt=)[^>]*>", s))
        if noalt: flags.append(f"{noalt} img without alt")
        if flags:
            problems += 1
            print(f"  {'(noindex) ' if noindex else ''}{f}: {', '.join(flags)}")
    return problems


if __name__ == "__main__":
    for f, cfg in PAGES.items():
        if os.path.exists(f): set_head(f, cfg)
    files = all_pages()
    pages = indexable(files)
    write_sitemap(pages); write_robots(); write_llms(pages)
    print(f"sitemap.xml: {len(pages)} pages | robots.txt | llms.txt")
    print("Audit (indexable pages must be clean; noindex pages are listed for later):")
    n = audit(files)
    print("  all clean" if not n else f"  {n} page(s) listed above")
