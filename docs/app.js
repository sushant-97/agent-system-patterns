/* Agent System Patterns — subtle UX enhancements.
   Progressive enhancement: the site works fully without this file.
   Adds: reading-progress bar, scroll-reveal, back-to-top, top-bar elevation. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var topbar = document.querySelector(".topbar");

  /* ---- Reading-progress bar (fills as you scroll) ---- */
  var progress = document.createElement("div");
  progress.className = "scroll-progress";
  progress.setAttribute("aria-hidden", "true");
  var progressFill = document.createElement("span");
  progress.appendChild(progressFill);
  document.body.appendChild(progress);

  /* ---- Back-to-top button ---- */
  var toTop = document.createElement("button");
  toTop.type = "button";
  toTop.className = "to-top";
  toTop.setAttribute("aria-label", "Back to top");
  toTop.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>';
  toTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });
  document.body.appendChild(toTop);

  /* ---- Scroll handler (rAF-throttled) ---- */
  var ticking = false;
  function update() {
    var doc = document.documentElement;
    var scrollTop = window.scrollY || doc.scrollTop || 0;
    var max = doc.scrollHeight - window.innerHeight;
    var pct = max > 0 ? Math.min(1, Math.max(0, scrollTop / max)) : 0;

    progressFill.style.transform = "scaleX(" + pct + ")";
    if (topbar) topbar.classList.toggle("scrolled", scrollTop > 8);
    toTop.classList.toggle("show", scrollTop > 500);
    ticking = false;
  }
  function onScroll() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  update();

  /* ---- Scroll reveal ---- */
  if (!reduceMotion && "IntersectionObserver" in window) {
    var selector = [
      ".post-card",
      ".section-head",
      ".article-banner",
      ".article-body > *",
      ".article-cta",
      ".article-related > .eyebrow",
      ".related-grid a"
    ].join(",");

    var items = Array.prototype.slice.call(document.querySelectorAll(selector));
    items.forEach(function (el) {
      el.classList.add("reveal");
    });

    var observer = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            obs.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.06 }
    );

    items.forEach(function (el) {
      observer.observe(el);
    });
  }
})();
