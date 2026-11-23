"""Builds schedule-a-demo/, demo/ and resources/ from the header and footer of blog/index.html.
Run from the repo root, then run tools/seo.py (it sets the SEO tags of these pages):

    python3 tools/build-pages.py && python3 tools/seo.py && npm run build

Resources: edit the guides / webinars / white papers lists below. Blog cards come from blog/<slug>/index.html
(every post that has assets/images/blog/<slug>/cover-800.webp), newest first.
"""
import re, html

blog = open("blog/index.html", encoding="utf-8").read()
head_end = blog.index("</head>")
header = blog[blog.index("<body"):blog.index('<main id="main">')]
footer = blog[blog.index("</main>") + len("</main>"):]

# Header and footer without "Blog" marked as the current page
# Blog isn't launched yet: no Blog in the top menu, and the footer link stays hidden (as on the other pages)
header = header.replace('          <li><a href="./" aria-current="page" class="border-b-2 border-brand-orange inline-block py-2 md:py-1">Blog</a></li>\n', '')
footer = footer.replace('<li><a href="./" aria-current="page" class="font-medium text-white">Blog</a></li>',
                        '<li class="hidden"><a href="../blog/" class="hover:text-white">Blog</a></li>')
assert 'Blog' not in header and 'aria-current' not in header and 'aria-current' not in footer

def head(title, desc, url):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t}</title>
  <meta name="description" content="{d}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="ZenOptics">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{url}">
  <link rel="icon" href="../assets/images/favicon.ico" sizes="any">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../style.css">
</head>
"""

CARD = "relative flex flex-col overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(30,48,95,0.08)] ring-1 ring-slate-200 transition hover:shadow-[0_12px_36px_rgba(30,48,95,0.16)] has-[a:focus-visible]:ring-2 has-[a:focus-visible]:ring-navy"
ARCS = """      <img src="../assets/images/imgi_52_circle.svg" alt="" aria-hidden="true" class="pointer-events-none absolute -top-24 -left-24 size-64">
      <img src="../assets/images/imgi_52_circle.svg" alt="" aria-hidden="true" class="pointer-events-none absolute -right-28 -bottom-24 size-80">"""

# ---------------- /schedule-a-demo/ ----------------
quotes = [
    ("slide-1-charles", "Analytics Leader", "My challenge is that not only do we have multiple BI tools (along with thousands of reports, spreadsheets, presentations, and PDFs) – sheer chaos. How do I rationalize and prioritize which reports to focus on?", "Charles W.", "Director of Analytics"),
    ("slide-2", "Supply Chain", "I have reports coming from our BI tools, our SaaS applications, our transportation and logistics partners, and a bunch of custom spreadsheets. Trying to find what we need, when we need it is daunting. How can I efficiently find the right information?", "Lucy B.", "Director of Supply Chain"),
    ("slide-6", "Analytics Leader", "We have invested in multiple analytics technologies, but many businesspeople aren’t using the tools. My challenge is how to remove frustrations and enable people to effectively create and use BI and analytics resources.", "Fernando R.", "Director, Data and Analytics"),
    ("slide-3", "Analytics Leader", "The CEO and Board need to better understand how data and analytics initiatives are yielding results and how to hit our strategic goals. I need visibility so I can understand how our tools are being utilized – and how to optimize them.", "Ana G.", "Chief Digital Officer"),
    ("slide-4", "Finance", "I am challenged with navigating the sheer volume of reports. It leaves me very little time for actual analysis. It would be great if all the reports were accessible through a single analytics portal to reduce the time spent on tedious activities.", "Raj P.", "Financial Planning & Analysis Analyst"),
    ("slide-5", "ESG Reporting", "With new regulations on ESG reporting, we need to do a better job of aggregating and managing the various reports. I am looking for a solution that allows me to define the workflows along with the associated reports, and efficiently share this with the team and our executives.", "Zoey M.", "Manager, ESG Reporting & Analytics"),
]
quote_cards = "\n".join(f"""          <li class="flex flex-col overflow-hidden rounded-2xl bg-white ring-1 ring-slate-200 shadow-[0_8px_30px_rgba(30,48,95,0.08)]">
            <img src="../assets/images/schedule-a-demo/{img}.webp" alt="" width="600" height="400" loading="lazy" decoding="async" data-fallback="hide" class="aspect-[3/2] w-full object-cover">
            <figure class="flex flex-1 flex-col p-6">
              <span class="text-xs font-semibold tracking-wider text-brand-blue uppercase">{html.escape(tag)}</span>
              <blockquote class="mt-3 flex-1 text-navy/85">“{html.escape(q)}”</blockquote>
              <figcaption class="mt-5 text-sm"><span class="font-semibold">{html.escape(n)}</span><br><span class="text-navy/70">{html.escape(r)}</span></figcaption>
            </figure>
          </li>""" for img, tag, q, n, r in quotes)

home = open("index.html", encoding="utf-8").read()
logos = re.findall(r'<img src="assets/images/(imgi_\d+_[^"]+)" alt="([^"]+)" data-fallback="text"', home[home.index("data-logo-slider"):home.index("</section>", home.index("data-logo-slider"))])
logo_items = "\n".join(f'          <li class="flex h-16 items-center justify-center px-2"><img src="../assets/images/{src}" alt="{alt}" data-fallback="text" loading="lazy" class="max-h-full w-auto max-w-[140px] object-contain grayscale"></li>' for src, alt in logos)

benefits = [
    "Unify their reports, dashboards, visualizations, data sets and documents in one single sign-on portal,",
    "Enable greater discoverability and access to the needed data and analytic assets,",
    "Enhance business process efficiency and productivity through analytic workflows, and",
    "Govern analytics to retire unused reports, identify duplicates and certify analytic assets.",
]
benefit_items = "\n".join(f'              <li class="flex gap-3"><svg class="mt-1 size-5 shrink-0 text-brand-orange" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg><span>{b}</span></li>' for b in benefits)

demo_main = f"""
    <!-- ============ HERO + DEMO FORM ============ -->
    <section class="relative overflow-hidden bg-navy text-white">
{ARCS}
      <div class="container-x relative grid items-start gap-10 py-14 sm:py-16 lg:grid-cols-2 lg:gap-14">
        <div>
          <h1 class="flex flex-wrap items-center gap-x-3 gap-y-2 text-3xl leading-tight font-semibold sm:text-[42px]">Discover <img src="../assets/images/imgi_42_footer-logo.svg" alt="ZenOptics" class="h-9 w-auto sm:h-11"></h1>
          <p class="mt-6 text-lg text-white/90">See and learn why ZenOptics Analytics Hub is chosen by data driven organizations to:</p>
          <ul class="mt-5 space-y-3 text-white/85">
{benefit_items}
          </ul>
          <a href="https://info.zenoptics.com/hubfs/Zenoptics-overview.mp4" target="_blank" rel="noopener" class="btn mt-8 border border-white/40 text-white hover:bg-white hover:text-navy">
            <svg class="size-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>
            Watch Overview
          </a>
        </div>
        <!-- Demo form: same HubSpot "Get a Demo" form as the popup. script.js loads it here because of data-demo-inline,
             and the Get Demo buttons on this page scroll to it instead of opening the popup. -->
        <div class="rounded-2xl bg-white p-6 text-navy shadow-2xl sm:p-8" id="demo-form">
          <h2 class="text-xl font-semibold sm:text-2xl">A member of our team will reach out to schedule your demo</h2>
          <div class="mt-6 min-h-[28rem]" id="hubspot-demo-form" data-demo-inline>
            <p class="py-10 text-center text-sm text-slate-500" data-hs-loading>Loading form…</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ WHAT LEADERS TELL US ============ -->
    <section class="container-x py-14 lg:py-20" aria-label="What analytics leaders tell us">
      <ul class="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
{quote_cards}
      </ul>
    </section>

    <!-- ============ CLIENT LOGOS ============ -->
    <section class="container-x pb-16 text-center">
      <h2 class="text-lg font-semibold sm:text-xl">Organizations Transforming their BI and Analytics with ZenOptics</h2>
      <ul class="mt-8 grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 lg:grid-cols-5" aria-label="Customer logos">
{logo_items}
      </ul>
    </section>
"""

# The popup isn't needed on this page: the form is in the page itself
_a = footer.index("  <!-- ============ GET DEMO MODAL ============ -->")
_b = footer.index('  <script src="../script.js">')
footer_no_demo_modal = footer[:_a] + footer[_b:]
assert 'id="demo-modal"' not in footer_no_demo_modal

page = (head("Schedule a Demo - Unify Analytics with ZenOptics",
             "Schedule a demo to see how ZenOptics unifies reports, dashboards, and analytics in a single portal, enhancing efficiency, governance, and data accessibility.",
             "https://zenoptics.com/schedule-a-demo/")
        + header + '<main id="main">\n' + demo_main + "\n  </main>" + footer_no_demo_modal)
open("schedule-a-demo/index.html", "w", encoding="utf-8").write(page)

# ---------------- /demo/ (old URL) -> /schedule-a-demo/ ----------------
# GitHub Pages can't do server redirects. This page forwards at once and keeps ?utm_... and #hash.
open("demo/index.html", "w", encoding="utf-8").write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Schedule a Demo | ZenOptics</title>
  <meta name="robots" content="noindex">
  <link rel="canonical" href="https://zenoptics.com/schedule-a-demo/">
  <!-- Old URL: forward to the demo page, keeping the campaign parameters (utm_...) -->
  <script>location.replace("../schedule-a-demo/" + location.search + location.hash);</script>
  <noscript><meta http-equiv="refresh" content="0; url=../schedule-a-demo/"></noscript>
  <style>body{font-family:Rubik,system-ui,sans-serif;color:#1e305f;padding:40px 16px;text-align:center;background:#fff}</style>
</head>
<body>
  <p>This page has moved. <a href="../schedule-a-demo/">Go to Schedule a Demo</a>.</p>
</body>
</html>
""")

# ---------------- /resources/ ----------------
def card(href, kind, title, text, external=False, cta="Open", img=None, video=False):
    """A resource card. img: cover in assets/images/resources/ (960x540). video: open the link in the page's video player."""
    tgt = ' target="_blank" rel="noopener"' if external and not video else ""
    vid = f' data-video="{href}"' if video else ""
    body = f'\n              <p class="mt-3 line-clamp-4 flex-1 text-navy/80">{html.escape(text)}</p>' if text else '\n              <div class="flex-1"></div>'
    play = ('\n              <span class="absolute right-3 bottom-3" aria-hidden="true"><span class="flex size-11 items-center justify-center rounded-full bg-navy/90 text-white shadow-lg ring-2 ring-white/70 transition group-hover:scale-110 group-hover:bg-brand-orange group-hover:text-navy">'
            '<svg class="ml-0.5 size-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></span></span>') if video else ""
    cover = (f'\n            <div class="relative">\n              <img src="../assets/images/resources/{img}.webp" alt="" width="960" height="540" loading="lazy" decoding="async" class="aspect-video w-full object-cover">{play}\n            </div>') if img else ""
    return f"""          <li class="group {CARD}">{cover}
            <div class="flex flex-1 flex-col p-6">
              <span class="text-xs font-semibold tracking-wider text-brand-blue uppercase">{kind}</span>
              <h3 class="mt-2 text-lg leading-snug font-semibold"><a href="{href}"{tgt}{vid} class="after:absolute after:inset-0 focus-visible:outline-none">{html.escape(title)}</a></h3>{body}
              <p class="mt-5 font-medium underline decoration-brand-orange decoration-2 underline-offset-4" aria-hidden="true">{cta}</p>
            </div>
          </li>"""

HS = "https://2836830.fs1.hubspotusercontent-na2.net/hubfs/2836830/"
guides = [
    card("../build-vs-buy-guide/", "Executive guide", "Build vs Buy: The portal you consider free is actually your most expensive system",
         "Your homegrown portal solved report discovery but lacked governance for KPIs and dashboard certification, which has led to annual compounding costs and inaccurate data for your copilots. This guide presents a build‑vs‑buy framework to address these issues.", cta="Read the guide", img="guide-build-vs-buy"),
    card("../bi-estate-assessment/", "Assessment", "BI Rationalization & BI Estate Assessment",
         "Identify reports to retain, consolidate or retire. Explore reporting maintenance costs and discuss a focused BI Estate Assessment with ZenOptics.", cta="Learn more", img="guide-bi-estate-assessment"),
    card("../trusted-ai/", "Workshop", "Trusted AI for Enterprise Analytics",
         "Help AI copilots and agents use the right KPI definitions, owners and governed analytics sources. Discuss a ZenOptics AI Context Workshop.", cta="Learn more", img="guide-trusted-ai"),
]
webinars = [
    ("How To Help Data Consumers Find What They’re Looking For", "https://info.zenoptics.com/hubfs/ZO_Zenoptics%20Partner%20Premium%20IQ%20webinar-_1.mp4"),
    ("How to Increase Analytics Adoption", HS + "Webinar%20Video/Increase%20Analytics%20Adoption%20webinar%20.mp4"),
    ("Streamlining Analytics and KPIs for Financial Services", HS + "VIDEO%20Streamlining%20Analytics%20and%20KPIs%20for%20Financial%20Services/_Streamlining%20Analytics%20and%20KPIs%20for%20Financial%20Services%20.mp4"),
    ("Increasing Adoption and Value of Data with An Analytics Catalog", HS + "Webinars/Zenoptics_IncreasingAdoption.mp4"),
    ("What is an Analytics Catalog?", HS + "Webinars/Analytics%20Catalog.mp4"),
    ("Brown-Forman Discusses their Analytics Catalog Journey and Demos their Implementation", HS + "Webinars/Webinar%20Brown%20Forman.mp4"),
    ("3 Ways to Boost Your Analytics Action Plan Today", HS + "Webinars/Webinar_3-Steps-Your-Analytics-Action-Plan-Needs-Today.mp4"),
]
WEBINAR_COVERS = ['data-consumers', 'increase-adoption', 'financial-services', 'adoption-catalog', 'what-is-catalog', 'brown-forman', '3-ways']  # assets/images/resources/webinar-<key>.webp, same order as the list above
webinar_cards = [card(u, "Webinar", t, "", cta="Watch the webinar", img="webinar-" + k, video=True) for (t, u), k in zip(webinars, WEBINAR_COVERS)]
paper_cards = [card(HS + "Whitepapers/Whitepaper_The-Power-of-Informed-Decision-Making.pdf", "White paper",
                    "The Power of Informed Decision Making", "", external=True, cta="Read the white paper", img="whitepaper-power-of-informed-decision-making")]

# Blog posts: every moved post that has a page and a cover (newest first), read from the post pages themselves
import glob as _glob, json as _json, datetime as _dt
def _post(f):
    s = open(f, encoding="utf-8").read()
    slug = f.split("/")[1]
    if not os.path.exists(f"assets/images/blog/{slug}/cover-800.webp"): return None
    ld = _json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    return dict(slug=slug, title=ld["headline"], date=ld["datePublished"], desc=ld.get("description", ""))
import os
posts = sorted(filter(None, (_post(f) for f in _glob.glob("blog/*/index.html"))), key=lambda p: p["date"], reverse=True)

def blog_card(p):
    d = _dt.date.fromisoformat(p["date"]).strftime("%B %-d, %Y")
    return f"""          <li class="{CARD}">
            <img src="../assets/images/blog/{p['slug']}/cover-800.webp" alt="" width="800" height="450" loading="lazy" decoding="async" class="aspect-video w-full object-cover">
            <div class="flex flex-1 flex-col p-6">
              <span class="text-xs font-semibold tracking-wider text-brand-blue uppercase">Blog</span>
              <h3 class="mt-2 text-lg leading-snug font-semibold"><a href="../blog/{p['slug']}/" class="after:absolute after:inset-0 focus-visible:outline-none">{html.escape(p['title'])}</a></h3>
              <p class="mt-3 line-clamp-3 flex-1 text-navy/80">{html.escape(p['desc'])}</p>
              <time datetime="{p['date']}" class="mt-5 text-sm text-navy/70">{d}</time>
            </div>
          </li>"""

blog_cards = [blog_card(p) for p in posts]

# key = URL hash, tab label, section heading, words for "View all …" / "See more …"
SECTIONS = [
    ("blog", "Blogs", "Blogs", "blogs", blog_cards),
    ("guides", "Guides", "Guides", "guides", guides),
    ("webinars", "Webinars", "Webinars", "webinars", webinar_cards),
    ("whitepapers", "White papers", "White papers", "white papers", paper_cards),
]
ARROW_R = '<svg class="size-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
ARROW_D = '<svg class="size-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>'
TAB = "shrink-0 rounded-full px-2.5 py-2 text-[13px] sm:px-4 sm:text-sm font-medium text-navy/80 transition hover:bg-white hover:text-navy aria-selected:bg-navy aria-selected:text-white"

tabs = "\n".join(
    [f'          <button type="button" role="tab" id="tab-all" aria-selected="true" data-res-tab="all" class="{TAB}">All</button>']
    + [f'          <button type="button" role="tab" id="tab-{k}" aria-selected="false" data-res-tab="{k}" class="{TAB}">{label}</button>' for k, label, *_ in SECTIONS])

def res_section(k, label, heading, word, cards):
    return f"""
    <section class="container-x pt-12 lg:pt-14" data-res-section="{k}" aria-labelledby="res-{k}-h">
      <div class="flex flex-wrap items-baseline justify-between gap-3">
        <h2 id="res-{k}-h" class="text-2xl font-semibold sm:text-3xl">{heading}</h2>
        <a href="#{k}" data-res-viewall="{k}" class="hidden items-center gap-1.5 font-medium text-navy underline decoration-brand-orange decoration-2 underline-offset-4 hover:decoration-navy">View all {word} {ARROW_R}</a>
      </div>
      <ul class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3" data-res-list>
{chr(10).join(cards)}
      </ul>
      <div class="mt-10 hidden justify-center" data-res-more-wrap>
        <button type="button" data-res-more class="btn border border-navy text-navy after:hidden hover:bg-navy hover:text-white">See more {word} {ARROW_D}</button>
      </div>
    </section>
"""

res_main = f"""
    <!-- ============ INTRO ============ -->
    <section class="relative overflow-hidden bg-navy text-white">
{ARCS}
      <div class="container-x relative py-14 sm:py-16">
        <h1 class="text-3xl leading-tight font-semibold [text-shadow:0_5px_19px_#1f7bc0] sm:text-[42px]">Resources</h1>
        <p class="mt-4 max-w-2xl text-lg text-white/85">Blogs, white papers and webinars to guide Analytics leaders and teams who desire to improve efficiency, productivity and value from their analytics investments.</p>
      </div>
    </section>

    <!-- ============ TABS (script.js: data-res-tabs). All = 6 cards per section; one tab = 9 cards, then 6 more per "See more".
         The tab is kept in the URL hash: #blog, #guides, #webinars, #whitepapers. ============ -->
    <div class="sticky top-[72px] z-30 border-b border-slate-200 bg-soft/95 backdrop-blur">
      <div class="overflow-x-auto">
        <div role="tablist" aria-label="Resource types" data-res-tabs class="mx-auto flex w-max gap-0 px-2 py-3 sm:gap-1 sm:px-4">
{tabs}
        </div>
      </div>
    </div>

    <!-- To add a resource: copy a card (<li>…</li>) in the right section and change the link, label and title. -->
    <div data-res-panels class="scroll-mt-[8.5rem] pb-16 lg:pb-20">
{"".join(res_section(*s) for s in SECTIONS)}
    </div>
"""

VIDEO_MODAL = """
  <!-- ============ VIDEO PLAYER (webinar cards; script.js data-video). No download button, no picture-in-picture. ============ -->
  <div id="video-modal" class="fixed inset-0 z-50 hidden items-center justify-center bg-black/90 p-4 sm:p-8" role="dialog" aria-modal="true" aria-labelledby="video-title">
    <div class="relative w-full max-w-5xl">
      <div class="mb-3 flex items-start justify-between gap-4">
        <h2 id="video-title" class="text-base font-medium text-white sm:text-lg" data-video-title></h2>
        <button type="button" data-video-close class="flex size-10 shrink-0 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20" aria-label="Close video">
          <svg class="size-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>
      <video class="aspect-video max-h-[80vh] w-full rounded-xl bg-black" controls controlslist="nodownload noremoteplayback" disablepictureinpicture disableremoteplayback playsinline preload="none" data-video-player></video>
    </div>
  </div>
"""
page = (head("Thought Leadership and Resource Library | ZenOptics",
             "Blogs, white papers and webinars to guide Analytics leaders and teams who desire to improve efficiency, productivity and value from their analytics investments.",
             "https://zenoptics.com/resources/")
        + header + '<main id="main">\n' + res_main + "\n  </main>" + VIDEO_MODAL + footer)
open("resources/index.html", "w", encoding="utf-8").write(page)
print("ok", len(logos), "logos")
