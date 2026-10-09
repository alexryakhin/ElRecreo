// El Recreo website: header shadow on scroll, reveal-on-scroll and the footer year.
// Everything works without it; this only adds polish. No analytics, no cookies, no storage.
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) document.documentElement.classList.add("js");

  var bar = document.querySelector(".bar");
  function onScroll() {
    if (bar) bar.classList.toggle("scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var items = document.querySelectorAll(".reveal");
  if (document.documentElement.classList.contains("js")) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.1 });
    items.forEach(function (item) { observer.observe(item); });
  }

  var year = String(new Date().getFullYear());
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = year; });
})();
