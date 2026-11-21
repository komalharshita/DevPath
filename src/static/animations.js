// DevPath UI motion enhancements.
// Keeps animations progressive: content stays visible if JavaScript is unavailable.

(function initDevPathAnimations() {
  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion) return;

  document.documentElement.classList.add("motion-enhanced");

  function markForReveal(selector, effect) {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(selector));
    nodes.forEach(function (node, index) {
      if (node.classList.contains("reveal-on-scroll")) return;
      node.classList.add("reveal-on-scroll");
      if (effect) node.classList.add(effect);
      node.style.setProperty("--reveal-delay", Math.min(index % 6, 5) * 70 + "ms");
    });
  }

  function revealNode(node) {
    node.classList.add("is-visible");
  }

  function observeRevealNodes(root) {
    var scope = root || document;
    var nodes = Array.prototype.slice.call(scope.querySelectorAll(".reveal-on-scroll:not(.is-visible)"));

    if (!("IntersectionObserver" in window)) {
      nodes.forEach(revealNode);
      return;
    }

    var observer = new IntersectionObserver(function (entries, entryObserver) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        revealNode(entry.target);
        entryObserver.unobserve(entry.target);
      });
    }, {
      root: null,
      rootMargin: "0px 0px -12% 0px",
      threshold: 0.12
    });

    nodes.forEach(function (node) {
      observer.observe(node);
    });
  }

  function setupRevealTargets() {
    markForReveal("main > section, main > header, main > .container, main > .project-page, main section, .admin-motion-surface, .error-page-inner");
    markForReveal(".section-eyebrow, .section-title, .section-sub");
    markForReveal(".hero-content > *", "reveal-left");
    markForReveal(".hero-visual > *", "reveal-right");
    markForReveal(".stat-card, .step-card, .feature-card, .feature-box, .project-card, .card, .saved-projects-panel, .profile-card, .badge-card, .achievement-card, .history-card, .leaderboard-card", "reveal-scale");
    markForReveal(".skill-strip-inner, .form-card-outer, .cta-inner, .footer-col, .app-footer__grid > *, .landing-footer .grid-cols-md-3 > *");
    markForReveal(".form-card form > .form-group, .form-card form > .skill-chips-row, .form-card form > .form-row, .form-actions");
    observeRevealNodes(document);
    document.addEventListener("focusin", function (event) {
      var revealTarget = event.target.closest && event.target.closest(".reveal-on-scroll");
      if (revealTarget) revealNode(revealTarget);
    });
  }

  function setupDynamicResultReveal() {
    var resultsGrid = document.getElementById("results-grid");
    if (!resultsGrid || !("MutationObserver" in window)) return;

    var mutationObserver = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        Array.prototype.slice.call(mutation.addedNodes).forEach(function (node, index) {
          if (!(node instanceof HTMLElement)) return;
          if (!node.classList.contains("project-card")) return;
          node.classList.add("reveal-on-scroll", "reveal-scale");
          node.style.setProperty("--reveal-delay", Math.min(index, 5) * 80 + "ms");
          window.requestAnimationFrame(function () {
            revealNode(node);
          });
        });
      });
    });

    mutationObserver.observe(resultsGrid, { childList: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      setupRevealTargets();
      setupDynamicResultReveal();
    });
  } else {
    setupRevealTargets();
    setupDynamicResultReveal();
  }
})();
