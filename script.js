// ---------- Footer year ----------
document.getElementById("year").textContent = new Date().getFullYear();

// ---------- Links that go nowhere for now ----------
document.addEventListener("click", (e) => {
  const link = e.target.closest('a[href="#"]');
  if (link) e.preventDefault();
});

// ---------- Image fallbacks ----------
// If a file in assets/images/ is missing, show a placeholder instead of a broken image.
//   data-fallback="text" -> show the alt text as a grey wordmark (logos)
//   data-fallback="hide" -> just hide the image (background photos)
//   (none)               -> grey box labelled with the alt text
function applyFallback(img) {
  const mode = img.dataset.fallback;
  if (mode === "hide") {
    img.style.display = "none";
    return;
  }
  const box = document.createElement("div");
  if (mode === "text") {
    box.className = "flex h-10 items-center text-2xl font-semibold tracking-wide text-slate-400";
  } else {
    box.className = img.className + " img-slot";
  }
  box.textContent = img.alt || "Image";
  img.replaceWith(box);
}

function watchImage(img) {
  if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) {
    applyFallback(img);
  } else {
    img.addEventListener("error", () => applyFallback(img), { once: true });
  }
}

document.querySelectorAll("img").forEach(watchImage);

// ---------- Mobile menu (burger) ----------
// Below the md breakpoint the main menu is hidden behind the burger button.
const menuToggle = document.querySelector("[data-menu-toggle]");
const mainMenu = document.getElementById("main-menu");
if (menuToggle && mainMenu) {
  const setMenu = (open) => {
    mainMenu.classList.toggle("hidden", !open);
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menuToggle.querySelector('[data-menu-icon="open"]').classList.toggle("hidden", open);
    menuToggle.querySelector('[data-menu-icon="close"]').classList.toggle("hidden", !open);
  };
  const isOpen = () => menuToggle.getAttribute("aria-expanded") === "true";
  menuToggle.addEventListener("click", () => setMenu(!isOpen()));
  // Close after choosing a link or the Get Demo button
  mainMenu.addEventListener("click", (e) => {
    if (e.target.closest("a, button")) setMenu(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isOpen()) {
      setMenu(false);
      menuToggle.focus();
    }
  });
  // Reset when the screen grows to desktop width
  matchMedia("(min-width: 48rem)").addEventListener("change", (e) => {
    if (e.matches) setMenu(false);
  });
}

// ---------- Modals (Get Demo + Contact Us) ----------
let lastFocus = null;

function openModal(modal) {
  lastFocus = document.activeElement;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
  modal.querySelector("[data-modal-close]").focus();
}

function closeModal(modal) {
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "";
  if (lastFocus) lastFocus.focus();
}

document.querySelectorAll("#demo-modal, #contact-modal").forEach((modal) => {
  modal.querySelector("[data-modal-close]").addEventListener("click", () => closeModal(modal));
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal(modal);
  });
});
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  document.querySelectorAll("#demo-modal.flex, #contact-modal.flex").forEach(closeModal);
});

// ---------- HubSpot forms ----------
// Each form is created in its target element; HubSpot renders it in an iframe with its own styling.
// Notifications, free-email blocking and spam protection are configured inside HubSpot.
const HUBSPOT = { portalId: "2836830", region: "na2" };
const HUBSPOT_FORMS = {
  demo: { formId: "8ec5cc1d-26a6-4c4a-97ea-061625dac864", target: "#hubspot-demo-form" },
  contact: {
    formId: "b172245c-51e8-4dea-b1a8-14e194863888",
    target: "#hubspot-contact-form",
    // CSS injected into HubSpot's iframe: hide the logo image the form has at the top
    iframeCss: ".hs-richtext:has(> img:only-child), .hs-richtext img { display: none !important; }",
  },
  newsletter: { formId: "bda34fd6-4283-416e-9952-b786b04059fb", target: "#hubspot-newsletter" },
};

let hubspotScript = null;
function loadHubSpotScript() {
  if (window.hbspt?.forms) return Promise.resolve();
  if (!hubspotScript) {
    hubspotScript = new Promise((resolve, reject) => {
      const el = document.createElement("script");
      el.src = "https://js-na2.hsforms.net/forms/embed/v2.js";
      el.charset = "utf-8";
      el.onload = () => (window.hbspt?.forms ? resolve() : reject());
      el.onerror = reject;
      document.head.appendChild(el);
    }).catch((e) => {
      hubspotScript = null; // allow a retry
      throw e;
    });
  }
  return hubspotScript;
}

// Add CSS inside a HubSpot form iframe (it is same-origin, so this is allowed)
function styleHubSpotIframe(box, css) {
  const doc = box.querySelector("iframe.hs-form-iframe")?.contentDocument;
  if (!doc || doc.getElementById("zo-iframe-css")) return;
  const style = doc.createElement("style");
  style.id = "zo-iframe-css";
  style.textContent = css;
  doc.head.appendChild(style);
}

const createdForms = new Set();
function showHubSpotForm(key) {
  const cfg = HUBSPOT_FORMS[key];
  const box = document.querySelector(cfg.target);
  if (!box || createdForms.has(key)) return;
  createdForms.add(key);
  const loading = box.querySelector("[data-hs-loading]");
  loadHubSpotScript()
    .then(() =>
      window.hbspt.forms.create({
        ...HUBSPOT,
        formId: cfg.formId,
        target: cfg.target,
        onFormReady: () => {
          loading?.remove();
          if (cfg.iframeCss) styleHubSpotIframe(box, cfg.iframeCss);
        },
      })
    )
    .catch(() => {
      createdForms.delete(key);
      if (loading) loading.textContent = "The form couldn’t load. Please check your connection and try again.";
    });
}

const demoModal = document.getElementById("demo-modal");
const contactModal = document.getElementById("contact-modal");
// On /schedule-a-demo/ the demo form sits in the page (data-demo-inline): load it now,
// and make the Get Demo buttons scroll to it instead of opening the popup.
const demoInline = document.querySelector("[data-demo-inline]");
if (demoInline) showHubSpotForm("demo");
document.querySelectorAll("[data-demo-open]").forEach((btn) =>
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    if (demoInline) {
      demoInline.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    openModal(demoModal);
    showHubSpotForm("demo");
  })
);
document.querySelectorAll("[data-contact-open]").forEach((btn) =>
  btn.addEventListener("click", () => { openModal(contactModal); showHubSpotForm("contact"); })
);

// Footer newsletter: load when the footer comes near the screen
const newsletterBox = document.querySelector(HUBSPOT_FORMS.newsletter.target);
if (newsletterBox) {
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { showHubSpotForm("newsletter"); io.disconnect(); }
    }, { rootMargin: "400px" });
    io.observe(newsletterBox);
  } else {
    showHubSpotForm("newsletter");
  }
}

// ---------- Case study carousel ----------
document.querySelectorAll("[data-carousel]").forEach((carousel) => {
  const slides = carousel.querySelectorAll("[data-slide]");
  let index = 0;

  function show(i) {
    index = (i + slides.length) % slides.length;
    slides.forEach((s, n) => {
      s.classList.toggle("opacity-0", n !== index);
      s.classList.toggle("pointer-events-none", n !== index);
    });
  }

  carousel.querySelector("[data-prev]").addEventListener("click", () => show(index - 1));
  carousel.querySelector("[data-next]").addEventListener("click", () => show(index + 1));
  if (slides.length < 2) carousel.querySelectorAll("[data-prev],[data-next]").forEach((b) => b.remove());
  show(0);
});

// ---------- Tabs ----------
document.querySelectorAll("[data-tabs]").forEach((tabList) => {
  const tabs = tabList.querySelectorAll("[data-tab]");
  const panels = tabList.parentElement.querySelectorAll("[data-panel]");

  function select(i) {
    tabs.forEach((t, n) => {
      const active = n === i;
      t.setAttribute("aria-selected", active);
      t.classList.toggle("border-brand-orange", active);
      t.classList.toggle("border-transparent", !active);
    });
    panels.forEach((p, n) => p.classList.toggle("hidden", n !== i));
  }

  tabs.forEach((t, i) => t.addEventListener("click", () => select(i)));
  select(0);
});

// ---------- Testimonials ----------
// summary = intro text (slightly darker italic); quote = the customer's own words (lighter italic).
// Text is copied exactly from the original site.
const testimonials = [
  {
    company: "Sysco Canada",
    name: "Jade Hollenbeck",
    role: "Senior Director of Business Intelligence",
    photo: "assets/images/imgi_58_Jade-Hollenbeck.webp",
    summary:
      "Sysco Canada's complex reporting environment made tracking catalogues, managing versions, and ensuring compliance time-consuming. Users struggled to find reports across multiple platforms, slowing access to trusted insights.",
    quote:
      "\"ZenOptics created a single, secure hub with intuitive search, one-click workflows, and collaborative features—enforcing security policies without impacting experience. The result: 26% of redundant reports retired, stronger governance, and an estimated 15–20% time savings. ZenOptics empowers our teams to focus on insights, not searching for reports.\"",
  },
  {
    company: "GAP Group",
    name: "Mark Emery",
    role: "Group Data & Analytics Manager",
    photo: "assets/images/imgi_59_slide-1-charles.webp",
    summary:
      "With the ZenOptics platform, GAP Group curated and streamlined their analytics environment to create a centralized place for business users to find and access trusted assets while improving the user experience.",
    quote:
      "\"GAP Group has been progressing through a data modernisation journey, transitioning from on-premises legacy systems to hybrid cloud solutions. Our previous reporting platform consisted of over 1,600 reports aggregating data from multiple systems. However, it was inflexible, outdated, and lacked user-friendliness.\"",
  },
  {
    company: "Brown Forman",
    name: "Gina Thornton",
    role: "Manager of Commercial Reporting and BI",
    photo: "assets/images/imgi_60_slide-3.webp",
    summary:
      "Our ongoing management of content is driven by ZenOptics… we use ZenOptics and the process we've built to keep everything in check. The process allowed us to identify important reports and how to make them more valuable and useful for users,”",
    quote:
      "“The benefits of this process are consistency and governance of reports, and eased discovery and access for end users.”",
  },
  {
    company: "Bimbo Bakeries USA",
    name: "Mike Katz",
    role: "Director of Business Intelligence Bimbo Bakeries",
    photo: "assets/images/imgi_61_zen-slide.webp",
    summary: "",
    quote:
      "\"By centralizing Manufacturing analytics into our One-Stop analytics intelligence platform powered by ZenOptics, we eliminated 25 separate SharePoint sites and created a single, consistent experience for 53 bakeries across Operations, Maintenance, Quality, HR, and Finance. Report discovery time improved by 5–10% for bakery teams and ~5% for the Operational Excellence team (OX), while publishing effort for OX was reduced by about 5 hours per month. The biggest win has been faster onboarding and training, giving teams reliable access to analytics with greater confidence in the data. ZenOptics helped improve our teams’ productivity by enabling them to work more efficiently, consistently, and with trust in their reporting.\"",
  },
  {
    company: "Illumina",
    name: "Obay Mouradi",
    role: "Director, Data Informatics",
    photo: "assets/images/imgi_62_zen-slide-2.webp",
    summary:
      "With ZenOptics, Illumina cleaned up and streamlined their analytics environment to create a centralized place for business users to find and access trusted assets.",
    quote:
      "“We had more than 10,000+ reports but no way to evaluate relevance, freshness, and reliable key reports over time. The project team was given a challenging task – to implement a one-stop-shop to search and browse reports and quickly find reliable key reports….that vision has come to fruition with an accessible platform along with a process that has identified the high-quality reports, now totaling just over 4,000 with 100+ key reports featured.”",
  },
  {
    company: "Janney",
    name: "Eric Seel",
    role: "BI manager at Janney Montgomery Scott",
    photo: "assets/images/imgi_63_slide-6.webp",
    summary:
      "ZenOptics improved discovery and access of reports and dashboards for end users at Janney Montgomery Scott. Further, Janney realized increased analytics governance and standardization.",
    quote:
      "“Prior to ZenOptics, we didn’t really have a way for colleagues to discover content, and those resources were isolated across multiple silos by application or department… We really wanted to simplify access for our users and essentially create one-stop-shopping. We needed a centralized catalog so users could find all our content, and we wanted to better manage and govern both our BI content and the underlying data terms, attributes, metrics, etc.”",
  },
];

const tSection = document.querySelector("[data-testimonials]");
if (tSection) {
  const thumbs = tSection.querySelector("[data-t-thumbs]");
  let current = 0;

  const buttons = testimonials.map((t, i) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className =
      "relative flex h-32 w-[calc(50%-0.5rem)] shrink-0 items-end overflow-hidden rounded-xl bg-neutral-500 px-3 pb-3 text-left text-[15px] leading-tight whitespace-nowrap text-white sm:h-[150px] sm:px-4 sm:pb-4 sm:text-xl md:w-[calc(25%-0.75rem)] md:text-[15px] lg:text-xl xl:text-[22px]";
    btn.innerHTML = `
      <img src="${t.photo}" alt="" data-fallback="hide" class="absolute inset-0 size-full object-cover object-right">
      <span class="absolute inset-0 bg-neutral-600/60 transition hover:bg-neutral-600/40"></span>
      <span class="pointer-events-none relative">${t.company}</span>`;
    btn.setAttribute("aria-label", "Show testimonial from " + t.company);
    btn.addEventListener("click", () => show(i));
    watchImage(btn.querySelector("img"));
    return btn;
  });

  const photo = tSection.querySelector("[data-t-photo]");

  function show(i) {
    const n = testimonials.length;
    current = (i + n) % n;
    const t = testimonials[current];
    tSection.querySelector("[data-t-name]").textContent = t.name;
    tSection.querySelector("[data-t-role]").textContent = t.role;
    tSection.querySelector("[data-t-summary]").textContent = t.summary;
    tSection.querySelector("[data-t-quote]").textContent = (t.summary && t.quote ? " " : "") + t.quote;
    photo.style.display = "";
    photo.alt = t.name;
    photo.onerror = () => (photo.style.display = "none");
    photo.src = t.photo;
    // Like the original: the selected company moves to the front, the rest follow in order.
    for (let k = 0; k < n; k++) thumbs.appendChild(buttons[(current + k) % n]);
    thumbs.scrollLeft = 0;
  }

  tSection.querySelector("[data-t-prev]").addEventListener("click", () => show(current - 1));
  tSection.querySelector("[data-t-next]").addEventListener("click", () => show(current + 1));
  show(0);
}

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---------- Client logo slider (one logo at a time, right to left) ----------
document.querySelectorAll("[data-logo-slider]").forEach((slider) => {
  const track = slider.querySelector("[data-track]");
  if (reduceMotion || track.children.length < 2) return;
  let paused = false;
  let moving = false;

  function step() {
    if (paused || moving || document.hidden) return;
    moving = true;
    const first = track.firstElementChild;
    const w = first.getBoundingClientRect().width;
    track.style.transition = "transform 0.8s ease";
    track.style.transform = `translateX(-${w}px)`;
    track.addEventListener(
      "transitionend",
      () => {
        track.style.transition = "none";
        track.appendChild(first); // move the logo that left the screen to the end
        track.style.transform = "translateX(0)";
        moving = false;
      },
      { once: true }
    );
  }

  slider.addEventListener("mouseenter", () => (paused = true));
  slider.addEventListener("mouseleave", () => (paused = false));
  setInterval(step, 2500);
});

// ---------- Stats counter (starts when the section scrolls into view) ----------
const counters = document.querySelectorAll("[data-count]");
if (counters.length && "IntersectionObserver" in window && !reduceMotion) {
  const run = (el) => {
    const target = Number(el.dataset.count);
    const suffix = el.dataset.suffix || "";
    const duration = 1600;
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out
      el.textContent = Math.round(target * eased) + suffix;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  counters.forEach((el) => (el.textContent = "0" + (el.dataset.suffix || "")));
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          run(e.target);
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.5 }
  );
  counters.forEach((el) => io.observe(el));
}

// ---------- 404 page: count down, then go to the home page ----------
const redirectCount = document.querySelector("[data-redirect-count]");
if (redirectCount) {
  let left = 5;
  const anyModalOpen = () => document.querySelector("#demo-modal.flex, #contact-modal.flex");
  const timer = setInterval(() => {
    if (anyModalOpen()) return; // pause while the visitor is filling a form
    left -= 1;
    redirectCount.textContent = String(Math.max(left, 0));
    if (left <= 0) {
      clearInterval(timer);
      window.location.replace("/");
    }
  }, 1000);
}

// ---------- Blog listing: show the first batch of posts, then one more batch per click ----------
// Every post is in the HTML (search engines and visitors without JavaScript see them all).
const postList = document.querySelector("[data-post-list]");
const showMoreWrap = document.querySelector("[data-show-more-wrap]");
if (postList && showMoreWrap) {
  const batch = Number(postList.dataset.batch) || 12;
  const items = Array.from(postList.children);
  let shown = batch;
  const update = () => {
    items.forEach((item, i) => item.classList.toggle("hidden", i >= shown));
    showMoreWrap.classList.toggle("hidden", shown >= items.length);
    showMoreWrap.classList.toggle("flex", shown < items.length);
  };
  showMoreWrap.querySelector("[data-show-more]").addEventListener("click", () => {
    const firstNew = items[shown];
    shown += batch;
    update();
    if (firstNew) firstNew.querySelector("a").focus(); // keyboard users continue from the first new post
  });
  update();
}

// ---------- Resources page: tabs (All / Blogs / Guides / Webinars / White papers) ----------
// All: every section, first 6 cards each, "View all …" when a section has more.
// One tab: only that section, first 9 cards, then "See more …" adds 6 at a time.
// The chosen tab is kept in the URL hash (#blog, #guides, #webinars, #whitepapers); All has no hash.
const resTabs = document.querySelector("[data-res-tabs]");
if (resTabs) {
  const ALL_COUNT = 6, TAB_COUNT = 9, STEP = 6;
  const tabs = Array.from(resTabs.querySelectorAll("[data-res-tab]"));
  const sections = Array.from(document.querySelectorAll("[data-res-section]"));
  const keys = sections.map((s) => s.dataset.resSection);
  const shown = {}; // cards shown per section in single-tab view

  const show = (el, on, display = "flex") => {
    el.classList.toggle("hidden", !on);
    el.classList.toggle(display, on);
  };

  const render = (key) => {
    tabs.forEach((t) => {
      const on = t.dataset.resTab === key;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
    });
    sections.forEach((sec) => {
      const k = sec.dataset.resSection;
      const items = Array.from(sec.querySelector("[data-res-list]").children);
      const viewAll = sec.querySelector("[data-res-viewall]");
      const moreWrap = sec.querySelector("[data-res-more-wrap]");
      if (key === "all") {
        sec.hidden = false;
        items.forEach((li, i) => li.classList.toggle("hidden", i >= ALL_COUNT));
        show(viewAll, items.length > ALL_COUNT);
        show(moreWrap, false);
      } else {
        sec.hidden = k !== key;
        if (k !== key) return;
        shown[k] = shown[k] || TAB_COUNT;
        items.forEach((li, i) => li.classList.toggle("hidden", i >= shown[k]));
        show(viewAll, false);
        show(moreWrap, shown[k] < items.length);
      }
    });
  };

  const keyFromHash = () => {
    const h = location.hash.slice(1);
    return keys.includes(h) ? h : "all";
  };

  const select = (key, scroll) => {
    history.pushState(null, "", key === "all" ? location.pathname + location.search : "#" + key);
    render(key);
    // bring the cards back to the top when the visitor had scrolled past them (or asked via "View all")
    const panels = document.querySelector("[data-res-panels]");
    if (scroll || panels.getBoundingClientRect().top < 0) panels.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  };

  tabs.forEach((t) =>
    t.addEventListener("click", () => {
      if (t.getAttribute("aria-selected") !== "true") delete shown[t.dataset.resTab]; // a tab opened again starts at 9 cards
      select(t.dataset.resTab, false);
    })
  );
  // Arrow keys move between tabs
  resTabs.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    const i = tabs.indexOf(document.activeElement);
    const next = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
    next.focus();
    next.click();
  });
  document.querySelectorAll("[data-res-viewall]").forEach((a) =>
    a.addEventListener("click", (e) => {
      e.preventDefault();
      delete shown[a.dataset.resViewall];
      select(a.dataset.resViewall, true);
    })
  );
  document.querySelectorAll("[data-res-more]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const sec = btn.closest("[data-res-section]");
      const k = sec.dataset.resSection;
      const items = Array.from(sec.querySelector("[data-res-list]").children);
      const from = shown[k];
      shown[k] += STEP;
      render(k);
      items.slice(from, shown[k]).forEach((li, i) => {
        li.classList.remove("res-reveal");
        void li.offsetWidth; // restart the animation
        li.style.animationDelay = reduceMotion ? "0ms" : `${(i % 3) * 70 + Math.floor(i / 3) * 90}ms`;
        li.classList.add("res-reveal");
      });
      items[from]?.querySelector("a")?.focus({ preventScroll: true }); // keyboard users continue from the first new card
    })
  );
  window.addEventListener("popstate", () => render(keyFromHash()));
  render(keyFromHash());
}

// ---------- Video player (webinar cards on Resources) ----------
// A link with data-video opens the video over a dark overlay instead of a new tab.
// The player has no download button, no picture-in-picture and no right-click menu.
const videoModal = document.getElementById("video-modal");
if (videoModal) {
  const player = videoModal.querySelector("[data-video-player]");
  const titleEl = videoModal.querySelector("[data-video-title]");
  const closeBtn = videoModal.querySelector("[data-video-close]");
  let opener = null;

  const closeVideo = () => {
    if (videoModal.classList.contains("hidden")) return;
    player.pause();
    player.removeAttribute("src");
    player.load(); // stop downloading the rest of the file
    videoModal.classList.add("hidden");
    videoModal.classList.remove("flex");
    document.documentElement.style.overflow = "";
    opener?.focus({ preventScroll: true });
  };

  document.querySelectorAll("a[data-video]").forEach((link) =>
    link.addEventListener("click", (e) => {
      e.preventDefault();
      opener = link;
      titleEl.textContent = link.textContent.trim();
      player.src = link.dataset.video;
      videoModal.classList.remove("hidden");
      videoModal.classList.add("flex");
      document.documentElement.style.overflow = "hidden";
      closeBtn.focus();
      player.play().catch(() => {}); // autoplay can be refused; the controls are there
    })
  );
  closeBtn.addEventListener("click", closeVideo);
  videoModal.addEventListener("click", (e) => {
    if (e.target === videoModal) closeVideo(); // click on the dark area
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeVideo();
    // keep Tab inside the player while it is open
    if (e.key === "Tab" && !videoModal.classList.contains("hidden")) {
      const items = [closeBtn, player];
      const i = items.indexOf(document.activeElement);
      e.preventDefault();
      items[(i + (e.shiftKey ? items.length - 1 : 1)) % items.length].focus();
    }
  });
  player.addEventListener("contextmenu", (e) => e.preventDefault());
}
