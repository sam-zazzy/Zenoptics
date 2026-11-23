// Renders branded title covers for blog posts that have no banner yet (used by tools/build-blog-archive.py).
// Usage: node tools/render-covers.js <list.json> <repo root>   (list: [{slug, title}])
// Needs playwright-core and Google Chrome. Writes assets/images/blog/<slug>/cover.png, then the build converts it to WebP.
const { chromium } = require("playwright-core");
const fs = require("fs"), path = require("path");
const [list, root] = process.argv.slice(2);
const items = JSON.parse(fs.readFileSync(list, "utf8"));
const b64 = (f) => fs.readFileSync(path.join(root, f)).toString("base64");
const logo = "data:image/svg+xml;base64," + b64("assets/images/imgi_42_footer-logo.svg");
const arc = "data:image/svg+xml;base64," + b64("assets/images/imgi_52_circle.svg");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

(async () => {
  const browser = await chromium.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  for (const { slug, title } of items) {
    await page.setContent(`<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@500;600&display=swap" rel="stylesheet">
<style>
  html,body{margin:0;width:1600px;height:900px;overflow:hidden}
  body{position:relative;font-family:Rubik,sans-serif;color:#fff;
       background:radial-gradient(circle at 85% 15%,#297bc0 0,transparent 45%),radial-gradient(circle at 10% 100%,#25bec6 0,transparent 35%),#1e305f}
  .arc{position:absolute;opacity:.9}
  .a1{width:520px;top:-170px;left:-170px}.a2{width:760px;right:-260px;bottom:-280px}
  .logo{position:absolute;left:120px;top:110px;height:64px}
  .bar{position:absolute;left:120px;top:250px;width:96px;height:10px;border-radius:5px;background:#ffb247}
  h1{position:absolute;left:120px;right:200px;top:300px;margin:0;font-weight:600;font-size:76px;line-height:1.12;text-shadow:0 6px 24px rgba(13,26,43,.45)}
  .tag{position:absolute;left:120px;bottom:100px;font-weight:500;font-size:30px;letter-spacing:.08em;text-transform:uppercase;color:#ffb247}
</style></head><body>
<img class="arc a1" src="${arc}"><img class="arc a2" src="${arc}">
<img class="logo" src="${logo}"><div class="bar"></div>
<h1 id="t">${esc(title)}</h1><div class="tag">ZenOptics Blog</div></body></html>`, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      await document.fonts.ready;
      const t = document.getElementById("t"); let s = 76;
      while (t.getBoundingClientRect().bottom > 760 && s > 40) { s -= 2; t.style.fontSize = s + "px"; }
    });
    await page.screenshot({ path: path.join(root, "assets/images/blog", slug, "cover.png") });
  }
  await browser.close();
})();
