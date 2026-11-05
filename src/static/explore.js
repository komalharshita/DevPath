/**
 * static/explore.js
 * Interactive Client-Side Behaviors for the DevPath Explore Page.
 *
 * Features:
 * 1. Quick-Filter Tech Stack chips bar (interactive filter triggers).
 * 2. Clickable skill badges on every card for instant tag filtering.
 * 3. Active filter pill tags with instant "✕" removal.
 * 4. Auto-submission on dropdown filter changes (Level, Interest, Skill, Time, Sort).
 * 5. Instant 0ms Quick-View Modal Preview with complete project overview & roadmap.
 * 6. Live In-Card Bookmarking with SVG fill animations & floating Toast notifications.
 */

(function () {
  "use strict";

  // Cache DOM elements
  var filterForm = document.getElementById("explore-filter-form");
  var quickViewModal = document.getElementById("project-quick-view-modal");
  var toastEl = document.getElementById("explore-toast");
  var toastMsgEl = document.getElementById("toast-message");
  var toastTimer = null;

  /* --------------------------------------------------------------------------
     Toast Notification Helper
     -------------------------------------------------------------------------- */
  function showToast(message) {
    if (!toastEl || !toastMsgEl) return;
    toastMsgEl.textContent = message;
    toastEl.classList.remove("hidden");

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toastEl.classList.add("hidden");
    }, 2500);
  }

  /* --------------------------------------------------------------------------
     URL Parameter Helper
     -------------------------------------------------------------------------- */
  function updateQueryParam(key, value) {
    var url = new URL(window.location.href);
    if (value) {
      url.searchParams.set(key, value);
    } else {
      url.searchParams.delete(key);
    }
    // Reset to page 1 whenever filters change
    url.searchParams.set("page", "1");
    window.location.href = url.toString();
  }

  function removeQueryParam(key) {
    var url = new URL(window.location.href);
    url.searchParams.delete(key);
    url.searchParams.set("page", "1");
    window.location.href = url.toString();
  }

  /* --------------------------------------------------------------------------
     Interactive Tech Stack Quick Chips
     -------------------------------------------------------------------------- */
  function initTechChips() {
    document.querySelectorAll("[data-skill-chip]").forEach(function (chip) {
      chip.addEventListener("click", function () {
        var skillVal = this.getAttribute("data-skill-chip");
        updateQueryParam("skill", skillVal);
      });
    });
  }

  /* --------------------------------------------------------------------------
     Clickable Skill Badges on Project Cards
     -------------------------------------------------------------------------- */
  function initClickableSkillBadges() {
    document.querySelectorAll("[data-filter-skill]").forEach(function (badge) {
      badge.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var skillVal = this.getAttribute("data-filter-skill");
        updateQueryParam("skill", skillVal);
      });
    });
  }

  /* --------------------------------------------------------------------------
     Active Filter Pills Dismissal ("✕")
     -------------------------------------------------------------------------- */
  function initActiveFilterPills() {
    document.querySelectorAll("[data-filter-key]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var filterKey = this.getAttribute("data-filter-key");
        removeQueryParam(filterKey);
      });
    });
  }

  /* --------------------------------------------------------------------------
     Auto-Submit Filter Selects on Change
     -------------------------------------------------------------------------- */
  function initAutoSubmitFilters() {
    if (!filterForm) return;

    var selects = filterForm.querySelectorAll("select");
    selects.forEach(function (sel) {
      sel.addEventListener("change", function () {
        // Reset page to 1 on filter change
        var pageInput = filterForm.querySelector("input[name='page']");
        if (pageInput) pageInput.value = "1";
        filterForm.submit();
      });
    });
  }

  /* --------------------------------------------------------------------------
     In-Card Bookmark / Quick-Save Handling
     -------------------------------------------------------------------------- */
  function initCardBookmarks() {
    if (typeof DevPathBookmarks === "undefined") return;

    document.querySelectorAll("[data-bookmark-project]").forEach(function (btn) {
      var projectId = btn.getAttribute("data-bookmark-project");
      var isSaved = DevPathBookmarks.isSaved(projectId);

      btn.classList.toggle("saved", isSaved);
      btn.setAttribute("aria-pressed", isSaved ? "true" : "false");

      var svg = btn.querySelector("svg");
      if (svg) svg.style.fill = isSaved ? "currentColor" : "none";

      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        // Retrieve project data from card json script
        var dataScript = document.querySelector("[data-project-json='" + projectId + "']");
        var projectData = null;
        if (dataScript) {
          try {
            projectData = JSON.parse(dataScript.textContent);
          } catch (err) {}
        }

        if (!projectData) {
          projectData = { id: projectId, title: "Project " + projectId };
        }

        DevPathBookmarks.toggle(projectData, btn);
        var currentlySaved = DevPathBookmarks.isSaved(projectId);

        btn.classList.toggle("saved", currentlySaved);
        btn.setAttribute("aria-pressed", currentlySaved ? "true" : "false");
        if (svg) svg.style.fill = currentlySaved ? "currentColor" : "none";

        showToast(currentlySaved ? "Saved to your bookmarks!" : "Removed from bookmarks");
      });
    });
  }

  /* --------------------------------------------------------------------------
     Quick View Modal Preview
     -------------------------------------------------------------------------- */
  var currentModalProjectId = null;

  function openQuickView(projectId) {
    if (!quickViewModal) return;

    var dataScript = document.querySelector("[data-project-json='" + projectId + "']");
    if (!dataScript) return;

    var project = null;
    try {
      project = JSON.parse(dataScript.textContent);
    } catch (err) {
      return;
    }

    currentModalProjectId = project.id;

    // Populate modal elements
    var titleEl = document.getElementById("modal-project-title");
    var descEl = document.getElementById("modal-project-description");
    var levelEl = document.getElementById("modal-project-level");
    var timeEl = document.getElementById("modal-project-time");
    var hoursEl = document.getElementById("modal-project-hours");
    var skillsContainer = document.getElementById("modal-project-skills");
    var featuresList = document.getElementById("modal-project-features");
    var roadmapList = document.getElementById("modal-project-roadmap");
    var fullLink = document.getElementById("modal-full-details-link");
    var modalBookmarkBtn = document.getElementById("modal-bookmark-btn");
    var modalBookmarkLabel = document.getElementById("modal-bookmark-label");

    if (titleEl) titleEl.textContent = project.title || "Project " + project.id;
    if (descEl) descEl.textContent = project.description || "No description provided.";
    if (levelEl) levelEl.textContent = project.level || "Any Level";
    if (timeEl) timeEl.textContent = "Time: " + (project.time || "Flexible");

    if (hoursEl) {
      if (project.estimated_hours) {
        hoursEl.textContent = "~" + project.estimated_hours + " hrs";
        hoursEl.style.display = "inline-flex";
      } else {
        hoursEl.style.display = "none";
      }
    }

    // Populate Skills
    if (skillsContainer) {
      skillsContainer.textContent = "";
      (project.skills || []).forEach(function (skill) {
        var badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = skill;
        skillsContainer.appendChild(badge);
      });
    }

    // Populate Features
    if (featuresList) {
      featuresList.textContent = "";
      var features = project.features || [];
      if (features.length) {
        features.forEach(function (feat) {
          var li = document.createElement("li");
          li.textContent = feat;
          featuresList.appendChild(li);
        });
        document.getElementById("modal-features-container").style.display = "block";
      } else {
        document.getElementById("modal-features-container").style.display = "none";
      }
    }

    // Populate Roadmap Preview (First 4 steps)
    if (roadmapList) {
      roadmapList.textContent = "";
      var roadmap = project.roadmap || [];
      if (roadmap.length) {
        roadmap.slice(0, 4).forEach(function (step) {
          var li = document.createElement("li");
          li.textContent = step;
          roadmapList.appendChild(li);
        });
        if (roadmap.length > 4) {
          var moreLi = document.createElement("li");
          moreLi.className = "text-muted";
          moreLi.textContent = "+ " + (roadmap.length - 4) + " more roadmap steps on full project page...";
          roadmapList.appendChild(moreLi);
        }
        document.getElementById("modal-roadmap-container").style.display = "block";
      } else {
        document.getElementById("modal-roadmap-container").style.display = "none";
      }
    }

    // Full Details Link
    if (fullLink && project.id) {
      fullLink.href = "/project/" + encodeURIComponent(project.id);
    }

    // Sync Modal Bookmark Button
    if (modalBookmarkBtn && typeof DevPathBookmarks !== "undefined") {
      var isSaved = DevPathBookmarks.isSaved(project.id);
      modalBookmarkBtn.classList.toggle("saved", isSaved);
      if (modalBookmarkLabel) {
        modalBookmarkLabel.textContent = isSaved ? "Saved" : "Save Project";
      }
      var svg = modalBookmarkBtn.querySelector("svg");
      if (svg) svg.style.fill = isSaved ? "currentColor" : "none";

      // Replace click handler cleanly
      var newBtn = modalBookmarkBtn.cloneNode(true);
      modalBookmarkBtn.parentNode.replaceChild(newBtn, modalBookmarkBtn);
      newBtn.addEventListener("click", function () {
        DevPathBookmarks.toggle(project, newBtn);
        var nowSaved = DevPathBookmarks.isSaved(project.id);
        newBtn.classList.toggle("saved", nowSaved);
        var label = newBtn.querySelector("#modal-bookmark-label");
        if (label) label.textContent = nowSaved ? "Saved" : "Save Project";
        var s = newBtn.querySelector("svg");
        if (s) s.style.fill = nowSaved ? "currentColor" : "none";

        // Sync card button if on current page
        var cardBtn = document.querySelector("[data-save-project-id='" + project.id + "']");
        if (cardBtn) {
          cardBtn.classList.toggle("saved", nowSaved);
          var cardSvg = cardBtn.querySelector("svg");
          if (cardSvg) cardSvg.style.fill = nowSaved ? "currentColor" : "none";
        }

        showToast(nowSaved ? "Saved to your bookmarks!" : "Removed from bookmarks");
      });
    }

    // Show modal
    quickViewModal.classList.remove("hidden");
    document.body.style.overflow = "hidden"; // prevent scroll behind
  }

  function closeQuickView() {
    if (!quickViewModal) return;
    quickViewModal.classList.add("hidden");
    document.body.style.overflow = "";
    currentModalProjectId = null;
  }

  function initQuickView() {
    document.querySelectorAll("[data-quick-view]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var projectId = this.getAttribute("data-quick-view");
        openQuickView(projectId);
      });
    });

    document.querySelectorAll("[data-close-modal]").forEach(function (el) {
      el.addEventListener("click", closeQuickView);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && quickViewModal && !quickViewModal.classList.contains("hidden")) {
        closeQuickView();
      }
    });
  }

  /* --------------------------------------------------------------------------
     Initialization
     -------------------------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", function () {
    initTechChips();
    initClickableSkillBadges();
    initActiveFilterPills();
    initAutoSubmitFilters();
    initCardBookmarks();
    initQuickView();
  });
})();
