/**
 * Finished Games — filter + lightbox (vanilla, no dependencies)
 *
 * Replaces the old jQuery + Isotope + Magnific Popup + imagesLoaded stack:
 * - Filtering is show/hide by platform class (CSS Grid handles layout).
 * - "Top 10" also orders visible cards by rank via the CSS `order` property.
 * - The lightbox is the native <dialog> (Esc / focus handled by the platform),
 *   navigating the currently-visible set with the arrow buttons or arrow keys.
 */
(function () {
  "use strict";

  var games = Array.prototype.slice.call(document.querySelectorAll(".game"));
  var filters = document.querySelectorAll(".filter");
  var empty = document.querySelector(".games__empty");

  // ---- Filtering ---------------------------------------------------------
  function applyFilter(f) {
    var visible = 0;
    games.forEach(function (g) {
      var show = f === "all"
        ? true
        : f === "top"
          ? g.classList.contains("is-top")
          : g.classList.contains(f);
      g.hidden = !show;
      // When showing the Top 10, order by rank; otherwise keep DOM order.
      g.style.order = f === "top" ? (g.dataset.rank || "999") : "";
      if (show) visible++;
    });
    if (empty) empty.hidden = visible > 0;
  }

  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filters.forEach(function (b) {
        b.classList.remove("is-active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-pressed", "true");
      applyFilter(btn.dataset.filter);
    });
  });

  // ---- Lightbox ----------------------------------------------------------
  var dlg = document.querySelector(".lightbox");
  if (!dlg || typeof dlg.showModal !== "function") return; // no dialog support: covers still open via… nothing; degrade to no-op

  var lbImg = dlg.querySelector(".lightbox__img");
  var lbTitle = dlg.querySelector(".lightbox__title");
  var lbSub = dlg.querySelector(".lightbox__sub");
  var group = [];
  var idx = 0;

  function render() {
    var b = group[idx];
    if (!b) return;
    lbImg.src = b.dataset.img;
    lbImg.alt = b.dataset.title;
    lbTitle.textContent = b.dataset.title;
    lbSub.textContent = b.dataset.sub;
  }

  function openFrom(btn) {
    group = games
      .filter(function (g) { return !g.hidden; })
      .map(function (g) { return g.querySelector(".game__open"); });
    idx = group.indexOf(btn);
    if (idx < 0) return;
    render();
    if (!dlg.open) dlg.showModal();
  }

  function move(delta) {
    if (!group.length) return;
    idx = (idx + delta + group.length) % group.length;
    render();
  }

  document.querySelectorAll(".game__open").forEach(function (btn) {
    btn.addEventListener("click", function () { openFrom(btn); });
  });

  dlg.querySelector(".lightbox__prev").addEventListener("click", function () { move(-1); });
  dlg.querySelector(".lightbox__next").addEventListener("click", function () { move(1); });
  dlg.querySelector(".lightbox__close").addEventListener("click", function () { dlg.close(); });

  // Click on the backdrop (the dialog element itself) closes.
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });

  document.addEventListener("keydown", function (e) {
    if (!dlg.open) return;
    if (e.key === "ArrowLeft") move(-1);
    else if (e.key === "ArrowRight") move(1);
  });
})();
