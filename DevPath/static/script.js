// script.js — DevPath client-side logic
//
// Responsibilities:
//   - Dark mode toggle
//   - Mobile navigation toggle
//   - Skill chip manager (add/remove skills)
//   - Form validation with per-field error messages
//   - Recommendation API call and loading states
//   - Result card rendering
//   - Code viewer panel (detail page)


// ============================================================
// THEME ENGINE
// ============================================================
// The theme system works in three parts:
//
//  Part A — Anti-FOUC inline script (in <head> of each template):
//    Sets html[data-theme] synchronously before the stylesheet is
//    evaluated, so the browser paints the correct colours on frame 1.
//
//  Part B — initTheme() (runs immediately below):
//    Syncs the toggle button aria-pressed + aria-label with the
//    already-applied theme. Adds the "theme-ready" class on the
//    next animation frame so CSS transitions become active only
//    AFTER the initial paint (preventing a colour transition flash
//    when the page first loads).
//
//  Part C — applyTheme(theme) (called on button click):
//    The single source of truth for all theme changes. Updates
//    data-theme, localStorage, aria-pressed, aria-label, and an
//    aria-live region so screen readers announce the change.
// ============================================================

(function () {

  // ---- Part B: sync button state once DOM is ready ----------
  function initTheme() {
    var html = document.documentElement;
    var theme = html.dataset.theme || "light";

    // Sync every toggle button on the page (desktop + mobile versions)
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      var isDark = theme === "dark";
      // aria-pressed = true when dark mode is ON
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      // aria-label describes what clicking WILL do (not what IS active),
      // which is the recommended accessible pattern for toggle buttons.
      btn.setAttribute("aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode"
      );
    });

    // Add .theme-ready on the NEXT frame so CSS transitions are
    // suppressed during the initial render (avoids colour flash).
    requestAnimationFrame(function () {
      html.classList.add("theme-ready");
    });
  }

  // ---- Part C: apply a theme change -------------------------
  function applyTheme(theme) {
    var html = document.documentElement;
    var isDark = theme === "dark";

    // 1. Apply via data attribute — CSS [data-theme="dark"] picks this up
    html.dataset.theme = theme;

    // 2. Persist the user's choice across sessions
    try { localStorage.setItem("theme", theme); } catch (e) { /* private browsing may block */ }

    // 3. Update every toggle button's accessible state
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      btn.setAttribute("aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode"
      );
    });

    // 4. Announce the change to screen readers via a visually-hidden
    //    aria-live="polite" region injected once into the DOM.
    var liveRegion = document.getElementById("theme-announce");
    if (!liveRegion) {
      liveRegion = document.createElement("span");
      liveRegion.id = "theme-announce";
      // Visually hidden but readable by screen readers
      liveRegion.setAttribute("role", "status");
      liveRegion.setAttribute("aria-live", "polite");
      liveRegion.style.cssText =
        "position:absolute;width:1px;height:1px;padding:0;overflow:hidden;" +
        "clip:rect(0,0,0,0);white-space:nowrap;border:0;";
      document.body.appendChild(liveRegion);
    }
    liveRegion.textContent = isDark ? "Dark mode enabled." : "Light mode enabled.";
  }


  document.addEventListener("click", function (evt) {
    var btn = evt.target.closest(".theme-toggle");
    if (!btn) return;
    var current = document.documentElement.dataset.theme || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme);
  } else {
    initTheme();
  }

}());


// ============================================================
// Dark Mode Toggle & Synchronization
// ============================================================
// UX Behavior Design Note:
// 1. System Preference Sync: By default, the application respects the OS dark/light mode settings
//    (using matchMedia("(prefers-color-scheme: dark)")).
// 2. Manual Override (Intentional UX Pattern): Once a user explicitly chooses a theme by clicking the toggle,
//    their manual preference is cached in localStorage. This manual choice intentionally takes precedence
//    over the system preferences to provide a stable, consistent theme across sessions.
// 3. System Re-sync: If the user wishes to revert back to system tracking, they can clear their browser data/localStorage.
//    The media query listener will automatically resume tracking system preferences when no localStorage key exists.
(function initTheme() {
  var toggle = document.getElementById("theme-toggle");
  var html = document.documentElement;
  var sunIcon = toggle && toggle.querySelector(".theme-toggle-sun");
  var moonIcon = toggle && toggle.querySelector(".theme-toggle-moon");

  function getPreferredTheme() {
    var saved = localStorage.getItem("theme");
    if (saved) return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function setTheme(theme) {
    html.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    if (toggle) {
      // Dynamic accessibility tracking using aria-pressed (true if dark mode is active)
      toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
      if (sunIcon && moonIcon) {
        if (theme === "dark") {
          sunIcon.style.display = "none";
          moonIcon.style.display = "inline";
        } else {
          sunIcon.style.display = "inline";
          moonIcon.style.display = "none";
        }
      }
    }
  }

  // Active theme is already initialized in <head> to prevent Flash of Unstyled Content (FOUC).
  // We sync buttons and accessibility attributes based on the current state.
  var activeTheme = html.getAttribute("data-theme") || getPreferredTheme();
  setTheme(activeTheme);

  if (toggle) {
    toggle.addEventListener("click", function () {
      var current = html.getAttribute("data-theme") || "light";
      setTheme(current === "dark" ? "light" : "dark");
    });
  }

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
    // Only sync dynamic system changes if no manual preference currently overrides it.
    if (!localStorage.getItem("theme")) {
      setTheme(e.matches ? "dark" : "light");
    }
  });
})();

// ============================================================
// Detect which page we are on
// ============================================================
// !! trick turns the DOM result into a simple true/false
var isIndexPage = !!document.getElementById("recommend-form");
// PROJECT_ID is set by the server only on detail pages, so if it's missing we're elsewhere
var isDetailPage = typeof PROJECT_ID !== "undefined";
var modal = document.getElementById('github-modal-overlay');
var openModalBtn = document.getElementById('btn-show-github'); // The trigger in your main form
var closeModalBtn = document.getElementById('btn-close-github');
var fetchBtn = document.getElementById('btn-fetch-github');
var githubInput = document.getElementById('github-username');
var errorMsg = document.getElementById('github-modal-error');

var STORAGE_KEY = "devpathUserProgress";
var progress = {
  searches: 0,
  projectViews: 0,
  codeOpens: 0,
  completions: 0,
  points: 0,
  viewedProjects: [],
  completedProjects: [],
  badges: {
    first_search: false,
    project_explorer: false,
    code_starter: false,
    completionist: false,
    roadmap_runner: false
  },
  achievements: [],
  bestScore: 0
};

var achievementToast = null;
var achievementToastTimeout = null;

function loadProgressState() {
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    var saved = JSON.parse(raw);
    if (saved && typeof saved === "object") {
      progress = Object.assign(progress, saved);
      progress.viewedProjects = Array.isArray(saved.viewedProjects) ? saved.viewedProjects : [];
      progress.completedProjects = Array.isArray(saved.completedProjects) ? saved.completedProjects : [];
      progress.achievements = Array.isArray(saved.achievements) ? saved.achievements : [];
      progress.badges = Object.assign(progress.badges, saved.badges || {});
    }
  } catch (err) {
    console.warn("Unable to load progress state", err);
  }
}

function saveProgressState() {
  try {
    progress.bestScore = Math.max(progress.bestScore, progress.points);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch (err) {
    console.warn("Unable to save progress state", err);
  }
}

function resetProgressState() {
  progress = {
    searches: 0,
    projectViews: 0,
    codeOpens: 0,
    completions: 0,
    points: 0,
    viewedProjects: [],
    completedProjects: [],
    badges: {
      first_search: false,
      project_explorer: false,
      code_starter: false,
      completionist: false,
      roadmap_runner: false
    },
    achievements: [],
    bestScore: 0
  };
  saveProgressState();
  updateProfileWidgets();
  showAchievementToast("Progress reset", "Your local profile has been cleared.");
}

function computeProgressPoints() {
  progress.points = progress.searches * 5 + progress.projectViews * 10 + progress.codeOpens * 15 + progress.completions * 30;
}

function addAchievement(title, description) {
  if (!title || !description) return;
  var exists = progress.achievements.some(function (achievement) { return achievement.title === title; });
  if (exists) return;

  progress.achievements.unshift({
    title: title,
    description: description,
    date: new Date().toLocaleDateString()
  });

  if (progress.achievements.length > 5) {
    progress.achievements.pop();
  }
}

function showAchievementToast(title, detail) {
  if (!achievementToast) {
    achievementToast = document.getElementById("achievement-toast");
  }
  if (!achievementToast) return;

  achievementToast.innerHTML = "<strong>" + title + "</strong>" +
    "<span>" + detail + "</span>";
  achievementToast.classList.add("show");

  clearTimeout(achievementToastTimeout);
  achievementToastTimeout = setTimeout(function () {
    achievementToast.classList.remove("show");
  }, 3200);
}

function updateProfileWidgets() {
  var pointsEl = document.getElementById("progress-points");
  var statsEl = document.getElementById("progress-stats");
  var meterFill = document.getElementById("progress-meter-fill");
  var badgesEl = document.getElementById("progress-badges");
  var achievementList = document.getElementById("achievement-list");
  var leaderboardList = document.getElementById("leaderboard-list");
  var historyList = document.getElementById("completed-history-list");
  var completionBtn = document.getElementById("btn-mark-complete");

  if (pointsEl) pointsEl.textContent = progress.points;
  if (statsEl) {
    statsEl.innerHTML =
      "<li><strong>Searches</strong><span>" + progress.searches + "</span></li>" +
      "<li><strong>Projects Viewed</strong><span>" + progress.projectViews + "</span></li>" +
      "<li><strong>Code Opens</strong><span>" + progress.codeOpens + "</span></li>" +
      "<li><strong>Projects Completed</strong><span>" + progress.completions + "</span></li>";
  }
  if (meterFill) {
    var percentage = Math.min(100, Math.round((progress.points / 250) * 100));
    meterFill.style.width = percentage + "%";
    meterFill.setAttribute("aria-valuenow", percentage);
    meterFill.textContent = percentage + "%";
  }

  if (badgesEl) {
    var badgeDefs = [
      {id: "first_search", label: "First Search", detail: "Run your first project search."},
      {id: "project_explorer", label: "Project Explorer", detail: "View a project detail page."},
      {id: "code_starter", label: "Code Starter", detail: "Open starter code."},
      {id: "completionist", label: "Completionist", detail: "Mark a project complete."},
      {id: "roadmap_runner", label: "Roadmap Runner", detail: "Search five times."}
    ];
    badgesEl.innerHTML = badgeDefs.map(function (badge) {
      var isUnlocked = progress.badges[badge.id];
      return "<li class=\"progress-badge " + (isUnlocked ? "progress-badge--unlocked" : "progress-badge--locked") + " title=\"" + badge.detail + "\">" +
        "<span class=\"badge-icon\">" + (isUnlocked ? "✓" : "☆") + "</span>" +
        "<span>" + badge.label + "</span>" +
        "</li>";
    }).join("");
  }

  if (achievementList) {
    if (progress.achievements.length === 0) {
      achievementList.innerHTML = "<li class=\"achievement-empty\">No achievements yet. Use DevPath and unlock the first badge.</li>";
    } else {
      achievementList.innerHTML = progress.achievements.map(function (achievement) {
        return "<li class=\"achievement-item\"><strong>" + achievement.title + "</strong>" +
          "<span>" + achievement.description + "</span>" +
          "<small>" + achievement.date + "</small></li>";
      }).join("");
    }
  }

  if (leaderboardList) {
    var ranked = getLeaderboardEntries();
    leaderboardList.innerHTML = ranked.map(function (entry, index) {
      return "<li><span>" + (index + 1) + ". " + entry.name + "</span>" +
        "<strong>" + entry.points + " pts</strong></li>";
    }).join("");
  }

  if (historyList) {
    if (progress.completedProjects.length === 0) {
      historyList.innerHTML = "<li class=\"achievement-empty\">No completed projects yet. Mark one complete from a project page.</li>";
    } else {
      historyList.innerHTML = progress.completedProjects.slice(0, 5).map(function (item) {
        var title = item && typeof item === "object" ? item.title : "Project " + item;
        return "<li><span>" + title + "</span><strong>Completed</strong></li>";
      }).join("");
    }
  }

  if (completionBtn) {
    var completed = projectIsCompleted(PROJECT_ID);
    completionBtn.textContent = completed ? "Project Completed" : "Mark Project Complete";
    completionBtn.disabled = completed;
  }
}

function projectIsCompleted(projectId) {
  if (!projectId) return false;
  return progress.completedProjects.some(function (item) {
    var id = item && typeof item === "object" ? item.id : item;
    return id === projectId;
  });
}

function getLeaderboardEntries() {
  var entries = [
    { name: "Ava", points: 245 },
    { name: "Kai", points: 192 },
    { name: "Sam", points: 176 },
    { name: "You", points: progress.points }
  ];
  return entries.sort(function (a, b) { return b.points - a.points; }).slice(0, 5);
}

function tryUnlockBadges() {
  if (progress.searches >= 1) {
    unlockBadge("first_search", "First Search", "You used DevPath to find your first project.");
  }
  if (progress.projectViews >= 1) {
    unlockBadge("project_explorer", "Project Explorer", "You viewed a project detail.");
  }
  if (progress.codeOpens >= 1) {
    unlockBadge("code_starter", "Code Starter", "You opened starter code.");
  }
  if (progress.completions >= 1) {
    unlockBadge("completionist", "Completionist", "You marked a project complete.");
  }
  if (progress.searches >= 5) {
    unlockBadge("roadmap_runner", "Roadmap Runner", "You searched five times.");
  }
}

function unlockBadge(id, title, detail) {
  if (progress.badges[id]) return;
  progress.badges[id] = true;
  addAchievement(title, detail);
  showAchievementToast("Badge unlocked", title + " — " + detail);
  saveProgressState();
  updateProfileWidgets();
}

function recordSearch() {
  progress.searches += 1;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

function recordProjectView() {
  if (typeof PROJECT_ID === "undefined") return;
  if (progress.viewedProjects.indexOf(PROJECT_ID) !== -1) return;
  progress.viewedProjects.push(PROJECT_ID);
  progress.projectViews = progress.viewedProjects.length;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

function recordCodeOpen() {
  progress.codeOpens += 1;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

function recordCompletion(projectId, projectTitle) {
  if (!projectId) return;
  if (projectIsCompleted(projectId)) {
    showAchievementToast("Already completed", "You've already marked this project complete.");
    return;
  }
  progress.completedProjects.push({
    id: projectId,
    title: projectTitle || "Project " + projectId
  });
  progress.completions = progress.completedProjects.length;
  computeProgressPoints();
  addAchievement("Completionist", "You finished a project and earned completion points.");
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

loadProgressState();
updateProfileWidgets();


// ============================================================
// Mobile navigation toggle (runs on all pages)
// ============================================================
(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle"); //hamburger button
  var menu   = document.getElementById("nav-mobile-menu"); //dropdown menu

  // Nothing to do if the nav isn't on this page, just bail out
  if (!toggle || !menu) return;

  toggle.addEventListener("click", function () {
    // classList.toggle returns true if class was added, false if removed
    var isOpen = menu.classList.toggle("open");
    toggle.classList.toggle("open", isOpen);
    // aria-expanded reflects whether the controlled menu is expanded
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    // Keep aria-expanded in sync so screen readers know if menu is open or closed
    toggle.setAttribute("aria-expanded", isOpen);
  });

  // Close menu when any mobile link is clicked
  menu.querySelectorAll(".nav-mobile-link").forEach(function (link) {
    link.addEventListener("click", function () {
      menu.classList.remove("open");
      toggle.classList.remove("open");
      // FIX: reset aria-expanded when menu closes via link click
      toggle.setAttribute("aria-expanded", "false");
    });
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth >= 640) {
      menu.classList.remove("open");
      toggle.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
})();


// ============================================================
// INDEX PAGE
// ============================================================
if (isIndexPage) {

  // DOM references
  // grabbing all the elements we'll need so we're not calling getElementById over and over again throughout the code
  var form              = document.getElementById("recommend-form");
  var submitBtn         = document.getElementById("submit-btn");
  var btnLabel          = document.getElementById("btn-label"); // "get recommendations" text
  var btnLoading        = document.getElementById("btn-loading"); // spinner icon inside the button
  var resultsSection    = document.getElementById("results-section");
  var resultsGrid       = document.getElementById("results-grid");
  var resultsLoadingEl  = document.getElementById("results-loading"); // "Loading..." text in the results
  var resultsEmptyEl    = document.getElementById("results-empty");
  var emptyMessageEl    = document.getElementById("empty-message");
  var skillsHidden      = document.getElementById("skills"); // the hidden input that holds skills list
  var skillsTextInput   = document.getElementById("skills-input"); //visible text box in which user types skills
  var chipsSelectedEl   = document.getElementById("skill-chips-selected"); //selected skills tags container
  var quickPickChips    = document.querySelectorAll(".skill-chip"); // predefined skills user can click

  // Tracks currently selected skills to prevent duplicates
  var selectedSkills = [];
  // Clear Filters Button Functionality
  var clearFiltersBtn = document.getElementById("clear-filters-btn");
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function () {
      var recommendForm = document.getElementById("recommend-form");
      if (recommendForm) {
        // 1. Reset standard form dropdowns and fields
        recommendForm.reset();

        // 2. Clear out the internal JavaScript array tracker completely
        selectedSkills = [];

        // 3. Clear the hidden inputs and visual chips using the file's own variables
        if (skillsHidden) skillsHidden.value = "";
        if (chipsSelectedEl) chipsSelectedEl.innerHTML = "";
        if (skillsTextInput) {
          skillsTextInput.value = "";
          skillsTextInput.focus(); // Place cursor back on input
        }

        // 4. Hide autocomplete suggestions if any are open
        var suggestionsBox = document.getElementById("skills-suggestions");
        if (suggestionsBox) suggestionsBox.innerHTML = "";

        // 5. Reset quick-pick chip visual active states if they have any
        if (quickPickChips) {
          quickPickChips.forEach(function (chip) {
            chip.classList.remove("active", "selected");
          });
        }
      }
    });
  }

var resetProgressBtn = document.getElementById("reset-progress-btn");
if (resetProgressBtn) {
  resetProgressBtn.addEventListener("click", resetProgressState);
}


  // ----------------------------------------------------------
  // Skill chip manager
  // ----------------------------------------------------------

  // Skills list for autocomplete (from skills.js)
  var availableSkills = [];
  if (typeof skills !== "undefined" && Array.isArray(skills) && skills.length > 0) {
    availableSkills = skills.map(function (s) { return s.label; });
  } else {
    // Fallback if skills.js doesn't load
    availableSkills = [
      "Python", "JavaScript", "Java", "C++", "HTML", "CSS", "React", "Node.js",
      "Django", "Flask", "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "Git",
      "C#", "Ruby", "PHP", "Go", "Swift", "TypeScript", "Angular", "Vue.js",
      "Spring", "Flutter", "TensorFlow", "PyTorch", "Data Science",
      "Machine Learning", "Artificial Intelligence", "DevOps", "Cybersecurity",
      "Blockchain", "UI/UX Design", "Game Development", "CI/CD", "REST API", "GraphQL",
      "Rust", "Kotlin"
    ];
  }

  var suggestionsDiv = document.getElementById("skills-suggestions");
  var skillWrap = document.getElementById("skill-input-wrap");
  var visibleSuggestions = [];
  var activeSuggestionIndex = -1;

  // Capture Enter key at the form level to avoid accidental submits
  // when the skills input is focused (some browsers can still submit).
  if (form && skillsTextInput) {
    form.addEventListener("keydown", function (evt) {
      if (evt.key === "Enter" && document.activeElement === skillsTextInput) {
        // Run in capture-phase to intercept before other handlers
        evt.preventDefault();
        evt.stopPropagation();

        if (activeSuggestionIndex >= 0 && visibleSuggestions[activeSuggestionIndex]) {
          selectSuggestion(visibleSuggestions[activeSuggestionIndex]);
          return;
        }

        if (skillsTextInput.value && skillsTextInput.value.trim()) {
          addSkill(skillsTextInput.value);
          skillsTextInput.value = "";
        }
        hideSuggestions();
      }
    }, true);
  }

  function initSkillStripMarquee() {
    var marquee = document.querySelector(".skill-strip-marquee");
    if (!marquee) return;
  }

  availableSkills = availableSkills.filter(function (skill, index, list) {
    return typeof skill === "string" && skill.trim() &&
      list.findIndex(function (item) {
        return item.toLowerCase() === skill.toLowerCase();
      }) === index;
  });

  if (suggestionsDiv) {
    suggestionsDiv.setAttribute("role", "listbox");
  }

  initSkillStripMarquee();

  function normalizeSkill(skill) {
    return skill.trim().toLowerCase();
  }

  function isSkillSelected(skill) {
    var normalizedSkill = normalizeSkill(skill);
    return selectedSkills.some(function (selectedSkill) {
      return normalizeSkill(selectedSkill) === normalizedSkill;
    });
  }

  function getCanonicalSkill(rawSkill) {
    var normalizedSkill = normalizeSkill(rawSkill);
    var matchedSkill = availableSkills.find(function (skill) {
      return normalizeSkill(skill) === normalizedSkill;
    });
    return matchedSkill || rawSkill.trim();
  }

  function getFilteredSkills(query) {
    var normalizedQuery = normalizeSkill(query);
    return availableSkills.filter(function (skill) {
      return normalizeSkill(skill).includes(normalizedQuery) && !isSkillSelected(skill);
    }).slice(0, 8);
  }

  function syncSuggestionsA11yState() {
    skillsTextInput.setAttribute("aria-expanded", visibleSuggestions.length > 0 ? "true" : "false");
  }

  function renderActiveSuggestion() {
    if (!suggestionsDiv) return;
    suggestionsDiv.querySelectorAll(".suggestion-item").forEach(function (item, index) {
      var isActive = index === activeSuggestionIndex;
      item.classList.toggle("suggestion-item--active", isActive);
      item.setAttribute("aria-selected", isActive ? "true" : "false");
    });
  }

  function hideSuggestions() {
    visibleSuggestions = [];
    activeSuggestionIndex = -1;
    if (suggestionsDiv) {
      suggestionsDiv.style.display = "none";
      suggestionsDiv.innerHTML = "";
    }
    syncSuggestionsA11yState();
  }

  function selectSuggestion(skill) {
    addSkill(skill);
    skillsTextInput.value = "";
    hideSuggestions();
    skillsTextInput.focus();
  }

  function displaySuggestions(items) {
    if (!suggestionsDiv) return;
    visibleSuggestions = items;
    activeSuggestionIndex = -1;
    if (items.length === 0) {
      hideSuggestions();
      return;
    }
    suggestionsDiv.innerHTML = "";
    items.forEach(function (skill, index) {
      var item = document.createElement("div");
      item.className = "suggestion-item";
      item.textContent = skill;
      item.setAttribute("role", "option");
      item.setAttribute("id", "skills-suggestion-" + index);
      item.setAttribute("aria-selected", "false");

      // Prevent the input blur handler from closing the menu before click runs.
      item.addEventListener("mousedown", function (evt) {
        evt.preventDefault();
      });

      item.addEventListener("mouseenter", function () {
        activeSuggestionIndex = index;
        renderActiveSuggestion();
      });

      item.addEventListener("click", function () {
        selectSuggestion(skill);
      });

      suggestionsDiv.appendChild(item);
    });
    suggestionsDiv.style.display = "block";
    syncSuggestionsA11yState();
  }

  function updateQuickPickState() {
    quickPickChips.forEach(function (chip) {
      var isActive = isSkillSelected(chip.getAttribute("data-skill") || "");
      chip.classList.toggle("active", isActive);
      chip.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }

  // Add skill on Enter key in the text input
  // when the user types a skill and hits Enter, add it we intercept Enter here so it doesn't accidentally submit the whole form
  skillsTextInput.addEventListener("keydown", function (evt) {
    if (evt.key === "ArrowDown" || evt.key === "ArrowUp") {
      if (visibleSuggestions.length === 0) {
        displaySuggestions(getFilteredSkills(skillsTextInput.value));
      }
      if (visibleSuggestions.length === 0) return;
      evt.preventDefault();
      if (evt.key === "ArrowDown") {
        activeSuggestionIndex = (activeSuggestionIndex + 1) % visibleSuggestions.length;
      } else {
        activeSuggestionIndex = activeSuggestionIndex <= 0
          ? visibleSuggestions.length - 1
          : activeSuggestionIndex - 1;
      }
      renderActiveSuggestion();
      return;
    }

    if (evt.key === "Escape") {
      hideSuggestions();
      return;
    }

    if (evt.key === "Enter") {
      evt.preventDefault();
      if (activeSuggestionIndex >= 0 && visibleSuggestions[activeSuggestionIndex]) {
        selectSuggestion(visibleSuggestions[activeSuggestionIndex]);
        return;
      }
      if (skillsTextInput.value.trim()) {
        addSkill(skillsTextInput.value);
        skillsTextInput.value = "";
      }
      hideSuggestions();
    }
  });

  // Add/toggle skill on quick-pick chip click
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");
      var isAlreadySelected = selectedSkills.some(function (s) {
        return s.toLowerCase() === skill.toLowerCase();
      });

      if (isAlreadySelected) {
        removeSkill(skill);
      } else {
        addSkill(skill);
      }
      hideSuggestions();
      skillsTextInput.value = "";
    });
  });

  // Show suggestions on input
  skillsTextInput.addEventListener("input", function (evt) {
    var typedValue = evt.target.value.trim();
    if (typedValue.length === 0) {
      hideSuggestions();
      return;
    }
    displaySuggestions(getFilteredSkills(typedValue));
  });

  skillsTextInput.addEventListener("focus", function () {
    if (skillsTextInput.value.trim()) {
      displaySuggestions(getFilteredSkills(skillsTextInput.value));
    }
  });

  // Hide suggestions when input loses focus
  skillsTextInput.addEventListener("blur", function () {
    setTimeout(function () { hideSuggestions(); }, 150);
  });

  if (skillWrap) {
    skillWrap.addEventListener("click", function () {
      skillsTextInput.focus();
    });
  }


  document.addEventListener("click", function (evt) {
    if (skillWrap && !skillWrap.contains(evt.target)) {
      hideSuggestions();
    }
  });

  //add a skill to the list if it's not empty or a duplicate
  function addSkill(rawSkill) {
    // Clean up any extra spaces and match to canonical skill name
    var skill = getCanonicalSkill(rawSkill);
    // Nothing to add if string is empty after trimming
    if (!skill) return;

    // Block duplicate entries (case-insensitive)
    if (isSkillSelected(skill)) return;

    selectedSkills.push(skill);
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    // Once a skill is added, remove the "please add a skill" error if it was showing
    clearFieldError("skills-error");
    // Ensure the corresponding quick-pick chip is visually active immediately
    try {
      var quickChip = document.querySelector('.skill-chip[data-skill="' + skill + '"]');
      if (quickChip) {
        quickChip.classList.add('active', 'selected');
        quickChip.setAttribute('aria-pressed', 'true');
      }
    } catch (e) {
      // ignore DOM errors
    }
    // Keep focus in the input so user can continue typing
    if (skillsTextInput) skillsTextInput.focus();
  }

  // remove a skill from the list and update the UI accordingly
  function removeSkill(skill) {
    // Rebuild the array without the skill that was just removed
    selectedSkills = selectedSkills.filter(function (selectedSkill) {
      return normalizeSkill(selectedSkill) !== normalizeSkill(skill);
    });
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    // Also clear the visual active state on the quick-pick chip if present
    try {
      var quickChip = document.querySelector('.skill-chip[data-skill="' + skill + '"]');
      if (quickChip) {
        quickChip.classList.remove('active', 'selected');
        quickChip.setAttribute('aria-pressed', 'false');
      }
    } catch (e) {
      // ignore DOM errors
    }
  }

  // recreate the selected skills chips based on the current array(selectedSkills)
  // called every time we add or remove a skill
  function renderSelectedChips() {
    // Wipe out old chips first so we don't end up with duplicates in the UI
    chipsSelectedEl.innerHTML = "";
    selectedSkills.forEach(function (skill) {
      // Create a new chip element for each selected skill
      var chipEl = document.createElement("span");
      chipEl.className = "skill-chip-selected";
      chipEl.textContent = skill;

      // Remove button for each chip (create lil "x" button)
      var removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "skill-chip-remove";
      removeBtn.innerHTML = "&times;"; //'x' symbol
      removeBtn.setAttribute("aria-label", "Remove " + skill);
      removeBtn.addEventListener("click", function (e) {
        // Stop click from bubbling up to the chip wrap's click listener
        e.stopPropagation();
        removeSkill(skill);
      });

      chipEl.appendChild(removeBtn); // put x button inside the chip
      chipsSelectedEl.appendChild(chipEl); //add chip to page
    });
  }

  function syncSkillsHiddenInput() {
    if (!skillsHidden) {
      skillsHidden = document.getElementById("skills");
    }
    // Keep the hidden input in sync for form serialisation
    if (skillsHidden) skillsHidden.value = selectedSkills.join(", ");
  }

  updateQuickPickState();


  // ----------------------------------------------------------
  // Form validation
  // ----------------------------------------------------------

  //puts error msg under specific field
  function showFieldError(fieldId, message) {
    var el = document.getElementById(fieldId);
    if (el) el.textContent = message;
  }

  //clears error msg under specific field
  function clearFieldError(fieldId) {
    var el = document.getElementById(fieldId);
    if (el) el.textContent = ""; //empty string = no error msg
  }

  //clears all error msgs in the form, called at the start of form submission to reset any previous errors
  function clearAllErrors() {
    ["skills-error", "level-error", "interest-error", "time-error"].forEach(clearFieldError);
    var generalErr = document.getElementById("form-error-general");
    if (generalErr) generalErr.textContent = "";
  }

  // checks form fields and shows error messages if any required field is missing or invalid. 
  // Returns true if the form is valid, false otherwise
  function validateForm() {
    var valid = true;

    // Check both the array and the hidden input since skills can come from either source
    if (selectedSkills.length === 0 && !skillsHidden.value.trim()) {
      showFieldError("skills-error", "Please add at least one skill.");
      valid = false;
    }
    if (!document.getElementById("level").value) {
      showFieldError("level-error", "Please select your experience level.");
      valid = false;
    }
    if (!document.getElementById("interest").value) {
      showFieldError("interest-error", "Please select an area of interest.");
      valid = false;
    }
    if (!document.getElementById("time").value) {
      showFieldError("time-error", "Please select your time availability.");
      valid = false;
    }

    return valid;
  }


  // ----------------------------------------------------------
  // Form submission and API call
  // ----------------------------------------------------------

  form.addEventListener("submit", function (evt) {
  evt.preventDefault();

  clearAllErrors();

  if (skillsTextInput.value.trim()) {
    addSkill(skillsTextInput.value);
    skillsTextInput.value = "";
    hideSuggestions();
  }

  if (!validateForm()) return;

  setLoadingState(true);

    requestAnimationFrame(function () {
      var payload = {
        skills: skillsHidden.value.trim() || skillsTextInput.value.trim(),
        level: document.getElementById("level").value,
        interest: document.getElementById("interest").value,
        time: document.getElementById("time").value
      };

      fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          setLoadingState(false);
          if (data.error) {
            var generalErr = document.getElementById("form-error-general");
            if (generalErr) generalErr.textContent = data.error;
            return;
          }
          renderResults(data.projects || [], data.message);
        })
        .catch(function () {
          setLoadingState(false);
          var generalErr = document.getElementById("form-error-general");
          if (generalErr) {
            generalErr.textContent = "An unexpected error occurred. Please try again.";
          }
        });
    });
  });

  // Manages the loading state of the form and results section(whats visible or not)
  function setLoadingState(isLoading) {
    // Disable the button so the user can't accidentally submit twice
    submitBtn.disabled = isLoading;
    submitBtn.setAttribute("aria-busy", isLoading);
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline-flex" : "none";

    if (isLoading) {
      // Show the results section with only the loading indicator visible
      resultsSection.style.display = "block";
      resultsLoadingEl.style.display = "block";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "none";
      // Scroll down so the user can see the spinner without manually scrolling
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } else {
      resultsLoadingEl.style.display = "none";
      resultsGrid.style.display = "grid"; //switch back to gird layout 
    }
  }


  // ----------------------------------------------------------
  // Render result cards
  // ----------------------------------------------------------

  function truncate(text, maxLength) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

  function createTag(text, type) {
    var span = document.createElement("span");
    span.className = "project-tag project-tag--" + type;
    span.textContent = text;
    return span;
  }

  function renderResults(projects, message) {
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    resultsGrid.innerHTML = "";
    recordSearch();

    if (!projects || projects.length === 0) {
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";
      
      var interestEl = document.getElementById("interest");
      var selectedInterest = interestEl ? interestEl.value : null;
      
      if (selectedInterest) {
        emptyMessageEl.textContent = "No projects are currently available for this interest. Please check back later or try a different area.";
      } else if (message) {
        emptyMessageEl.textContent = message;
      } else {
        emptyMessageEl.textContent = "Try adjusting your skills or choosing a different interest area.";
      }
      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    resultsEmptyEl.style.display = "none";
    resultsGrid.style.display = "grid";
    projects.forEach(function (project) {
      resultsGrid.appendChild(buildProjectCard(project));
    });
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  function buildProjectCard(project) {
    var card = document.createElement("div");
    card.className = "project-card";

    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;

    var desc = document.createElement("p");
    desc.className = "project-card-desc";
    var descText = document.createElement("span");
    descText.className = "project-card-desc-text";
    var shortText = truncate(project.description, 120);
    var fullText = project.description;
    var isExpanded = false;
    descText.textContent = shortText;
    desc.appendChild(descText);

    if (fullText && fullText.length > 120) {
      var readMoreBtn = document.createElement("button");
      readMoreBtn.className = "read-more-btn";
      readMoreBtn.textContent = "Read more";
      readMoreBtn.setAttribute("aria-expanded", "false");
      readMoreBtn.addEventListener("click", function () {
        isExpanded = !isExpanded;
        descText.textContent = isExpanded ? fullText : shortText;
        readMoreBtn.textContent = isExpanded ? "Read less" : "Read more";
        readMoreBtn.setAttribute("aria-expanded", isExpanded ? "true" : "false");
      });
      desc.appendChild(readMoreBtn);
    }

    var tagsRow = document.createElement("div");
    tagsRow.className = "project-card-tags";
    (project.skills || []).forEach(function (skill) {
      tagsRow.appendChild(createTag(skill, "skill"));
    });
    tagsRow.appendChild(createTag(project.level, (project.level || "").toLowerCase()));
    tagsRow.appendChild(createTag("Time: " + project.time, "time"));

    var footer = document.createElement("div");
    footer.className = "project-card-footer";
    var link = document.createElement("a");
    link.className = "btn-details";
    link.textContent = "View Full Project";
    link.href = "/project/" + project.id;
    footer.appendChild(link);

    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tagsRow);
    card.appendChild(footer);
    return card;
  }

} // end isIndexPage


  // ============================================================
  // DETAIL PAGE
  // ============================================================
  if (isDetailPage) {

    var codePanel = document.getElementById("code-panel"); // sliding panel that shows the starter code "
    var codePanelOverlay = document.getElementById("code-panel-overlay"); // background overlay 
    var codeContentEl = document.getElementById("code-content"); // <pre> element inside the panel where the code will be inserted
    var codePanelFilename = document.getElementById("code-panel-filename"); // filename display
    var btnViewCode = document.getElementById("btn-view-code"); // button to open the code panel on desktop
    var btnViewCodeSm = document.getElementById("btn-view-code-sm"); // button to open the code panel on mobile (could be the same button with different styling, but we have two here for simplicity)
    var btnClosePanel = document.getElementById("code-panel-close"); // button inside the panel to close it

    // Cache flag so code is only fetched once per page load
    var codeFetched = false;

    //opens the sliding code panel 
    function openCodePanel() {
      // Panel element might not exist on every detail page, so check first
      if (!codePanel) return;
      codePanel.classList.add("active");
      if (codePanelOverlay) codePanelOverlay.classList.add("active");
      // Lock background scroll so the page doesn't scroll behind the panel
      document.body.style.overflow = "hidden";

      // Only fetch the code on the first open, no need to re-fetch every time
      if (!codeFetched) fetchStarterCode();
    }

    //closes the code panel and hides the overlay
    function closeCodePanel() {
      if (!codePanel) return;
      codePanel.classList.remove("active");
      if (codePanelOverlay) codePanelOverlay.classList.remove("active");
      // Restore normal scrolling once the panel is closed
      document.body.style.overflow = "";
    }

    // Render code string as a list of DOM rows where each row contains a
    // line-number gutter cell and a code cell. Returning DOM nodes instead
    // of an HTML string avoids innerHTML XSS risks from the code content.
    function renderCodeWithLineNumbers(code) {
      var lines = (code || "").split("\n");
      return lines.map(function (line, index) {
        var row = document.createElement("div");
        row.className = "code-line";

        var lineNum = document.createElement("span");
        lineNum.className = "code-line-number";
        lineNum.setAttribute("aria-hidden", "true");
        lineNum.textContent = index + 1;

        var lineCode = document.createElement("span");
        lineCode.className = "code-line-content";
        lineCode.textContent = line;

        row.appendChild(lineNum);
        row.appendChild(lineCode);
        return row;
      });
    }

    //fetches the starter code from the server via an API call
    //inserts the code into the panel and handles loading/error states
    function fetchStarterCode() {
      // Show a loading message while we wait for the API response
      if (codeContentEl) codeContentEl.textContent = "Loading starter code...";

      fetch("/project/" + PROJECT_ID + "/code")
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.error) {
            if (codeContentEl) codeContentEl.textContent = "Error: " + data.error;
            return;
          }
          if (codePanelFilename) codePanelFilename.textContent = data.filename;
          if (codeContentEl) {
            codeContentEl.textContent = "";
            renderCodeWithLineNumbers(data.code).forEach(function (row) {
              codeContentEl.appendChild(row);
            });
          }
          // Mark as fetched so we don't hit the API again on the next open
          codeFetched = true;
        })
        .catch(function () {
          if (codeContentEl) {
            codeContentEl.textContent = "Could not load starter code. Try downloading it instead.";
          }
        });
    }

   // ============================================================
// ROADMAP PROGRESS TRACKER
// ============================================================


var roadmapCheckboxes = document.querySelectorAll(
    ".roadmap-checkbox"
);

var progressFill = document.getElementById(
    "roadmap-progress-fill"
);

var progressText = document.getElementById(
    "roadmap-progress-text"
);

var progressBar = document.querySelector(
    ".roadmap-progress-bar"
);

// Local storage key
var roadmapStorageKey =
    `devpath-roadmap-progress-${PROJECT_ID}`;


// ------------------------------------------------------------
// Restore saved roadmap state
// ------------------------------------------------------------

var savedRoadmapState =
    localStorage.getItem(
        roadmapStorageKey
    );

if(savedRoadmapState){

    try{

        var parsedState =
            JSON.parse(savedRoadmapState);

        roadmapCheckboxes.forEach(
            function(cb,index){

                cb.checked =
                    !!parsedState[index];

            }
        );

    } catch(error){

        console.error(
            "Failed to restore roadmap progress",
            error
        );

    }
}


// ------------------------------------------------------------
// Update roadmap progress
// ------------------------------------------------------------

function updateRoadmapProgress(){

    if(!roadmapCheckboxes.length){
        return;
    }

    var completed = 0;

    roadmapCheckboxes.forEach(function(cb){

        var step = cb.closest(
            ".roadmap-step"
        );

        if(cb.checked){

            completed++;

            if(step){
                step.classList.add(
                    "completed"
                );
            }

        } else {

            if(step){
                step.classList.remove(
                    "completed"
                );
            }

        }

    });

    var percent = Math.round(
        (completed / roadmapCheckboxes.length)
        * 100
    );

    // Update progress bar fill
    if(progressFill){

        progressFill.style.width =
            percent + "%";

    }

    // Update progress text
    if(progressText){

        progressText.textContent =
            percent + "% completed";

    }

    // Accessibility update
    if(progressBar){

        progressBar.setAttribute(
            "aria-valuenow",
            percent
        );

    }

    // Save checkbox state
    var savedState = [];

    roadmapCheckboxes.forEach(function(cb){

        savedState.push(
            cb.checked
        );

    });

    localStorage.setItem(
        roadmapStorageKey,
        JSON.stringify(savedState)
    );

}


// ------------------------------------------------------------
// Attach checkbox listeners
// ------------------------------------------------------------

roadmapCheckboxes.forEach(function(cb){

    cb.addEventListener(
        "change",
        updateRoadmapProgress
    );

});


// ------------------------------------------------------------
// Initial progress render
// ------------------------------------------------------------

updateRoadmapProgress();

    // Attach open/close handlers
    if (btnViewCode) btnViewCode.addEventListener("click", openCodePanel);
    if (btnViewCodeSm) btnViewCodeSm.addEventListener("click", openCodePanel);
    if (btnClosePanel) btnClosePanel.addEventListener("click", closeCodePanel);

    if (codePanelOverlay) {
      codePanelOverlay.addEventListener("click", closeCodePanel); //clicking on the background overlay to also close the panel
    }

    // Let keyboard users close the panel with Escape — important for accessibility
    document.addEventListener("keydown", function (evt) {
      if (evt.key === "Escape") closeCodePanel(); //esc key to close
    });

    // ----------------------------------------------------------
    // Copy Code button
    // ----------------------------------------------------------
    var btnCopyCode = document.getElementById("btn-copy-code");
    var copyToast = document.getElementById("copy-toast"); //popup msg when copied 
    var toastTimeout = null;

    //shows the "copied to clipboard" state on the button and the toast message, then resets after a short delay
    function showCopySuccess() {
      if (!btnCopyCode) return;

      // Swap icons on the button(copy and checkmark icons)
      var copyIcon = btnCopyCode.querySelector(".copy-icon");
      var checkIcon = btnCopyCode.querySelector(".check-icon");
      var btnLabel = btnCopyCode.querySelector(".copy-btn-label");

      if (copyIcon) copyIcon.style.display = "none";
      if (checkIcon) checkIcon.style.display = "inline";
      if (btnLabel) btnLabel.textContent = "Copied!";
      btnCopyCode.classList.add("copied");
      // Disable button so user can't spam click it while toast is showing
      btnCopyCode.disabled = true;

      // Show toast
      if (copyToast) {
        copyToast.classList.add("show");
      }

      // Auto-reset after 2.5 s
      // Clear any previous timeout first so timers don't stack up
      clearTimeout(toastTimeout);
      toastTimeout = setTimeout(function () {
        if (copyIcon) copyIcon.style.display = "inline";
        if (checkIcon) checkIcon.style.display = "none";
        if (btnLabel) btnLabel.textContent = "Copy Code";
        btnCopyCode.classList.remove("copied");
        btnCopyCode.disabled = false;
        if (copyToast) copyToast.classList.remove("show");
      }, 2500);
    }

    if (btnCopyCode) {
      btnCopyCode.addEventListener("click", function () {
        var code = codeContentEl
          ? Array.from(codeContentEl.querySelectorAll(".line-content"))
            .map(function (el) { return el.textContent; })
            .join("\n")
          : "";
        // Don't copy if the code hasn't loaded yet — just ignore the click
        if (!code || code === "Loading..." || code === "Loading starter code...") return;

        // Use Clipboard API with textarea fallback
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(code).then(showCopySuccess).catch(function () {
            fallbackCopy(code); // clipboard api failed, try the old way
          });
        } else {
          fallbackCopy(code); // Clipboard API not supported, use fallback method
        }
      });
    }

    // Fallback method to copy text using a hidden textarea and execCommand (for older browsers)
    function fallbackCopy(text) {
      // Some older browsers don't support navigator.clipboard, so we use a hidden textarea instead
      var ta = document.createElement("textarea");
      ta.value = text;
      // Push it off-screen so it's not visible but can still be selected
      ta.style.cssText = "position:fixed;top:-9999px;left:-9999px;opacity:0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      // execCommand is old and deprecated but works as a last resort — fail silently if it doesn't
      try { document.execCommand("copy"); showCopySuccess(); } catch (e) { /* silent fail */ }
      document.body.removeChild(ta);
    }
  } // end isDetailPage

if (isIndexPage) {
  if (
    openModalBtn &&
    closeModalBtn &&
    modal &&
    githubInput &&
    fetchBtn &&
    errorMsg
  ) {
    // Opens the GitHub input modal and focuses the input field
    openModalBtn.addEventListener("click", function(e) {
      e.preventDefault();
      modal.classList.add("active");
      githubInput.focus();
    });

    // Closes the GitHub input modal and resets its values and errors
    var closeGithubModal = function() {
      modal.classList.remove("active");
      githubInput.value = "";
      errorMsg.textContent = "";
    };

    closeModalBtn.addEventListener("click", closeGithubModal);

    // Closes the modal if the user clicks the background overlay outside the card
    modal.addEventListener("click", function(e) {
      if (e.target === modal) closeGithubModal();
    });

    // Fetches repositories for a GitHub user and adds unique languages to the skills list
    fetchBtn.addEventListener("click", function() {
      var username = githubInput.value.trim();

      // Clear any previous error before validating / retrying
      errorMsg.textContent = "";

      if (!username) {
        errorMsg.textContent = "Please enter a GitHub username";
        githubInput.focus();
        return;
      }

      fetchBtn.disabled = true;
      fetchBtn.textContent = "Syncing...";

      fetch("https://api.github.com/users/" + encodeURIComponent(username) + "/repos")
        .then(function(response) {
          if (!response.ok) {
            if (response.status === 404) {
              throw new Error("Username not found. Please check and try again.");
            }
            if (response.status === 403) {
              throw new Error("GitHub rate limit reached. Please try again later.");
            }
            throw new Error("Failed to fetch skills. Please try again.");
          }
          return response.json();
        })
        .then(function(repos) {
          var langs = [];
          for (var i = 0; i < repos.length; i++) {
            var lang = repos[i].language;
            if (lang && langs.indexOf(lang) === -1) {
              langs.push(lang);
            }
          }

          if (langs.length > 0) {
            for (var j = 0; j < langs.length; j++) {
              if (typeof addSkill === "function") addSkill(langs[j]);
            }
            closeGithubModal();
          } else {
            errorMsg.textContent = "No public languages found.";
          }
          fetchBtn.disabled = false;
          fetchBtn.textContent = "Fetch Skills";
        })
        .catch(function(err) {
          errorMsg.textContent = err.message || "Failed to fetch skills";
          fetchBtn.disabled = false;
          fetchBtn.textContent = "Fetch Skills";
        });
    });
  } // end github modal handlers
}


// ============================================================
// SCROLL NAVIGATION BUTTON (runs on all pages)
// ============================================================
(function () {
  var SCROLL_THRESHOLD = 200;
  var scrollTopBtn = document.getElementById('scroll-top-btn');
  var scrollBtnIcon = document.getElementById('scroll-btn-icon');
  var atBottom = false;

  var ARROW_UP   = '<polyline points="18 15 12 9 6 15"/>';
  var ARROW_DOWN = '<polyline points="6 9 12 15 18 9"/>';

  function isNearBottom() {
    return (window.innerHeight + window.pageYOffset) >= document.body.scrollHeight - 40;
  }

  function handleScroll() {
    if (!scrollTopBtn) return;
    if (window.pageYOffset > SCROLL_THRESHOLD) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
    if (isNearBottom()) {
      atBottom = true;
      scrollTopBtn.setAttribute('aria-label', 'Scroll to top');
      scrollTopBtn.title = 'Scroll to top';
      if (scrollBtnIcon) scrollBtnIcon.innerHTML = ARROW_UP;
    } else {
      atBottom = false;
      scrollTopBtn.setAttribute('aria-label', 'Scroll to bottom');
      scrollTopBtn.title = 'Scroll to bottom';
      if (scrollBtnIcon) scrollBtnIcon.innerHTML = ARROW_DOWN;
    }
  }

  if (scrollTopBtn) {
    window.addEventListener('scroll', handleScroll, { passive: true });
    scrollTopBtn.addEventListener('click', function () {
      if (atBottom) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }
    });
    handleScroll();
  }

})();
