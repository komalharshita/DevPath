// DevPath client-side behavior.
// Compatibility key for bookmarks.js: "devpathSavedProjects"

(function () {
  var html = document.documentElement;

  function applyTheme(theme) {
    var isDark = theme === "dark";
    html.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("theme", theme);
    } catch (err) {
      // Storage can be unavailable in private browsing.
    }

    document.querySelectorAll(".theme-toggle").forEach(function (button) {
      button.setAttribute("aria-pressed", isDark ? "true" : "false");
      button.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    });

    // Sync preview cards active styles
    var cards = document.querySelectorAll(".theme-preview-card");
    cards.forEach(function (card) {
      if (card.getAttribute("data-theme-target") === theme) {
        card.style.borderColor = "var(--accent)";
      } else {
        card.style.borderColor = "var(--border)";
      }
    });
  }

  function initTheme() {
    var theme = "light";

    try {
      theme = localStorage.getItem("theme") || html.getAttribute("data-theme") || "light";
    } catch (err) {
      theme = html.getAttribute("data-theme") || "light";
    }

    applyTheme(theme);

    requestAnimationFrame(function () {
      html.classList.add("theme-ready");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    // Inject the theme modal HTML dynamically
    var modalHtml = `
<div id="theme-preview-modal" class="theme-modal-overlay" aria-hidden="true" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:10000; backdrop-filter:blur(4px); align-items:center; justify-content:center;">
  <div class="theme-modal-content" role="dialog" aria-modal="true" aria-labelledby="theme-modal-title" style="background:var(--surface); border:1px solid var(--border); border-radius:var(--r-lg); padding:1.5rem; max-width:500px; width:90%; box-shadow:var(--shadow-xl);">
    <div class="theme-modal-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
      <h2 id="theme-modal-title" style="font-size:1.25rem; margin:0; color:var(--text-heading);">Choose a Theme</h2>
      <button id="close-theme-modal" aria-label="Close modal" style="background:transparent; border:none; font-size:1.5rem; cursor:pointer; color:var(--text-muted);">&times;</button>
    </div>
    <div class="theme-preview-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
      <!-- Light Theme Card -->
      <button class="theme-preview-card" data-theme-target="light" style="background:transparent; border:2px solid var(--border); border-radius:var(--r-md); padding:1rem; cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:1rem; transition:all 0.2s ease;">
        <div class="preview-mockup" style="width:100%; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:8px; display:flex; flex-direction:column; gap:6px;">
          <div style="width:100%; height:12px; background:#e2e8f0; border-radius:3px;"></div>
          <div style="width:100%; height:6px; background:#cbd5e1; border-radius:2px;"></div>
          <div style="width:60%; height:6px; background:#cbd5e1; border-radius:2px;"></div>
          <div style="width:100%; margin-top:4px; padding:4px 0; background:#3b82f6; border-radius:3px; color:#fff; font-size:8px; text-align:center; font-weight:bold;">Button</div>
        </div>
        <span class="preview-label" style="font-weight:600; color:var(--text-heading);">Light Theme</span>
      </button>
      
      <!-- Dark Theme Card -->
      <button class="theme-preview-card" data-theme-target="dark" style="background:transparent; border:2px solid var(--border); border-radius:var(--r-md); padding:1rem; cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:1rem; transition:all 0.2s ease;">
        <div class="preview-mockup" style="width:100%; background:#0f172a; border:1px solid #1e293b; border-radius:6px; padding:8px; display:flex; flex-direction:column; gap:6px;">
          <div style="width:100%; height:12px; background:#1e293b; border-radius:3px;"></div>
          <div style="width:100%; height:6px; background:#334155; border-radius:2px;"></div>
          <div style="width:60%; height:6px; background:#334155; border-radius:2px;"></div>
          <div style="width:100%; margin-top:4px; padding:4px 0; background:#60a5fa; border-radius:3px; color:#0f172a; font-size:8px; text-align:center; font-weight:bold;">Button</div>
        </div>
        <span class="preview-label" style="font-weight:600; color:var(--text-heading);">Dark Theme</span>
      </button>
    </div>
  </div>
</div>
    `;
    document.body.insertAdjacentHTML("beforeend", modalHtml);

    var modal = document.getElementById("theme-preview-modal");
    var closeBtn = document.getElementById("close-theme-modal");
    var cards = document.querySelectorAll(".theme-preview-card");

    function closeModal() {
      if (modal) {
        modal.style.display = "none";
        modal.setAttribute("aria-hidden", "true");
      }
    }

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (modal) {
      modal.addEventListener("click", function (e) {
        if (e.target === modal) closeModal();
      });
    }

    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        var theme = this.getAttribute("data-theme-target");
        applyTheme(theme);
        setTimeout(closeModal, 150);
      });
      card.addEventListener("mouseenter", function () {
        if (this.getAttribute("data-theme-target") !== html.getAttribute("data-theme")) {
          this.style.borderColor = "var(--gray-400)";
        }
      });
      card.addEventListener("mouseleave", function () {
        if (this.getAttribute("data-theme-target") !== html.getAttribute("data-theme")) {
          this.style.borderColor = "var(--border)";
        }
      });
    });

    // Update active styles on modal load
    var currentTheme = html.getAttribute("data-theme") || "light";
    cards.forEach(function (card) {
      if (card.getAttribute("data-theme-target") === currentTheme) {
        card.style.borderColor = "var(--accent)";
      } else {
        card.style.borderColor = "var(--border)";
      }
    });
  });

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest(".theme-toggle");
    if (!toggle) return;
    event.preventDefault();
    var modal = document.getElementById("theme-preview-modal");
    if (modal) {
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    }
  });

  initTheme();
})();

(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu = document.getElementById("nav-mobile-menu");
  if (!toggle || !menu) return;

  function setOpen(isOpen) {
    menu.classList.toggle("open", isOpen);
    toggle.classList.toggle("open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    document.body.style.overflow = isOpen ? "hidden" : "";
  }

  toggle.addEventListener("click", function () {
    setOpen(!menu.classList.contains("open"));
  });

  menu.querySelectorAll(".nav-mobile-link").forEach(function (link) {
    link.addEventListener("click", function () {
      setOpen(false);
    });
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth >= 640) setOpen(false);
  });
})();

var POINTS_PER_SEARCH     = 5;
var POINTS_PER_VIEW       = 10;
var POINTS_PER_CODE_OPEN  = 15;
var POINTS_PER_COMPLETION = 30;

var PROGRESS_TARGET_SEARCHES     = 10;
var PROGRESS_TARGET_VIEWS        = 10;
var PROGRESS_TARGET_CODE_OPENS   = 10;
var PROGRESS_TARGET_COMPLETIONS  = 5;

var PROGRESS_MAX_POINTS = (
  PROGRESS_TARGET_SEARCHES * POINTS_PER_SEARCH +
  PROGRESS_TARGET_VIEWS * POINTS_PER_VIEW +
  PROGRESS_TARGET_CODE_OPENS * POINTS_PER_CODE_OPEN +
  PROGRESS_TARGET_COMPLETIONS * POINTS_PER_COMPLETION
);

var STORAGE_KEY = "devpathUserProgress";
var progress = {
  searches: 0,
  projectViews: 0,
  codeOpens: 0,
  completions: 0,
  points: 0,
  viewedProjects: [],
  completedProjects: [],
  achievements: [],
  badges: {
    first_search: false,
    project_explorer: false,
    code_starter: false,
    completionist: false,
    roadmap_runner: false
  },
  bestScore: 0
};

// Points awarded per action
var POINTS_PER_SEARCH     = 5;
var POINTS_PER_VIEW       = 10;
var POINTS_PER_CODE_OPEN  = 15;
var POINTS_PER_COMPLETION = 30;

var PROGRESS_TARGET_SEARCHES     = 10;
var PROGRESS_TARGET_VIEWS        = 10;
var PROGRESS_TARGET_CODE_OPENS   = 10;
var PROGRESS_TARGET_COMPLETIONS  = 5;

// Maximum achievable points given the targets above
var PROGRESS_MAX_POINTS = (
  PROGRESS_TARGET_SEARCHES    * POINTS_PER_SEARCH     +   // 50
  PROGRESS_TARGET_VIEWS       * POINTS_PER_VIEW       +   // 100
  PROGRESS_TARGET_CODE_OPENS  * POINTS_PER_CODE_OPEN  +   // 150
  PROGRESS_TARGET_COMPLETIONS * POINTS_PER_COMPLETION     // 150
);  // total = 450

function loadProgressState() {
  try {
    var saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (!saved || typeof saved !== "object") return;
    progress = Object.assign(progress, saved);
    progress.viewedProjects = Array.isArray(saved.viewedProjects) ? saved.viewedProjects : [];
    progress.completedProjects = Array.isArray(saved.completedProjects) ? saved.completedProjects : [];
    progress.achievements = Array.isArray(saved.achievements) ? saved.achievements : [];
    progress.badges = Object.assign(progress.badges, saved.badges || {});
  } catch (err) {
    console.warn("Unable to load progress state", err);
  }
}

function saveProgressState() {
  try {
    progress.bestScore = Math.max(progress.bestScore || 0, progress.points || 0);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch (err) {
    console.warn("Unable to save progress state", err);
  }
}

function computeProgressPoints() {
  progress.points = progress.searches * POINTS_PER_SEARCH + progress.projectViews * POINTS_PER_VIEW +
    progress.codeOpens * POINTS_PER_CODE_OPEN + progress.completions * POINTS_PER_COMPLETION;
}

function showAchievementToast(title, detail) {
  var toast = document.getElementById("achievement-toast");
  if (!toast) return;
  toast.textContent = "";
  var strong = document.createElement("strong");
  strong.textContent = title;
  var span = document.createElement("span");
  span.textContent = detail;
  toast.appendChild(strong);
  toast.appendChild(span);
  toast.classList.add("show");
  window.clearTimeout(showAchievementToast.timeout);
  showAchievementToast.timeout = window.setTimeout(function () {
    toast.classList.remove("show");
  }, 3200);
}

function addAchievement(title, detail) {
  if (progress.achievements.some(function (item) { return item.title === title; })) return;
  progress.achievements.unshift({
    title: title,
    description: detail,
    date: new Date().toLocaleDateString()
  });
  progress.achievements = progress.achievements.slice(0, 5);
}

function unlockBadge(id, title, detail) {
  if (progress.badges[id]) return;
  progress.badges[id] = true;
  addAchievement(title, detail);
  showAchievementToast("Badge unlocked", title + " - " + detail);
}

function tryUnlockBadges() {
  if (progress.searches >= 1) unlockBadge("first_search", "First Search", "You used DevPath to find your first project.");
  if (progress.projectViews >= 1) unlockBadge("project_explorer", "Project Explorer", "You viewed a project detail.");
  if (progress.codeOpens >= 1) unlockBadge("code_starter", "Code Starter", "You opened starter code.");
  if (progress.completions >= 1) unlockBadge("completionist", "Completionist", "You marked a project complete.");
  if (progress.searches >= 5) unlockBadge("roadmap_runner", "Roadmap Runner", "You searched five times.");
}

function projectIsCompleted(projectId) {
  return progress.completedProjects.some(function (item) {
    return (item && typeof item === "object" ? item.id : item) === projectId;
  });
}

function updateProfileWidgets() {
  var pointsEl = document.getElementById("progress-points");
  var statsEl = document.getElementById("progress-stats");
  var meterFill = document.getElementById("progress-meter-fill");
  var meterLabel = document.getElementById("progress-meter-label");
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
    var percentage = Math.min(100, Math.round((progress.points / PROGRESS_MAX_POINTS) * 100));
    meterFill.style.width = percentage + "%";
    meterFill.setAttribute("aria-valuenow", String(percentage));
    if (meterLabel) meterLabel.textContent = percentage + "%";
  }
  if (badgesEl) {
    var badges = [
      ["first_search", "First Search"],
      ["project_explorer", "Project Explorer"],
      ["code_starter", "Code Starter"],
      ["completionist", "Completionist"],
      ["roadmap_runner", "Roadmap Runner"]
    ];
    badgesEl.innerHTML = badges.map(function (badge) {
      var unlocked = progress.badges[badge[0]];
      return "<li class=\"progress-badge " + (unlocked ? "progress-badge--unlocked" : "progress-badge--locked") +
        "\"><span class=\"badge-icon\">" + (unlocked ? "OK" : "*") + "</span><span>" + badge[1] + "</span></li>";
    }).join("");
  }
  if (achievementList) {
    achievementList.innerHTML = progress.achievements.length
      ? progress.achievements.map(function (item) {
        return "<li class=\"achievement-item\"><strong>" + item.title + "</strong><span>" +
          item.description + "</span><small>" + item.date + "</small></li>";
      }).join("")
      : "<li class=\"achievement-empty\">No achievements yet. Use DevPath and unlock the first badge.</li>";
  }
  if (leaderboardList) {
    var entries = [
      { name: "Ava", points: 245 },
      { name: "Kai", points: 192 },
      { name: "Sam", points: 176 },
      { name: "You", points: progress.points }
    ].sort(function (a, b) { return b.points - a.points; });
    leaderboardList.innerHTML = entries.map(function (entry, index) {
      return "<li><span>" + (index + 1) + ". " + entry.name + "</span><strong>" + entry.points + " pts</strong></li>";
    }).join("");
  }
  if (historyList) {
    historyList.innerHTML = progress.completedProjects.length
      ? progress.completedProjects.slice(0, 5).map(function (item) {
        var title = item && typeof item === "object" ? item.title : "Project " + item;
        return "<li><span>" + title + "</span><strong>Completed</strong></li>";
      }).join("")
      : "<li class=\"achievement-empty\">No completed projects yet. Mark one complete from a project page.</li>";
  }
  if (completionBtn && typeof PROJECT_ID !== "undefined") {
    var completed = projectIsCompleted(PROJECT_ID);
    if (completed) {
      completionBtn.textContent = "Project Completed";
      completionBtn.disabled = true;
    } else {
      var checkboxes = document.querySelectorAll(".roadmap-checkbox");
      var total = checkboxes.length;
      var checkedCount = 0;
      for (var i = 0; i < total; i++) {
        if (checkboxes[i].checked) checkedCount++;
      }
      if (total > 0 && checkedCount === total) {
        completionBtn.textContent = "Mark Project Complete";
        completionBtn.disabled = false;
      } else {
        completionBtn.textContent = "Complete All Steps First";
        completionBtn.disabled = true;
      }
    }
  }
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
  if (progress.viewedProjects.indexOf(PROJECT_ID) === -1) {
    progress.viewedProjects.push(PROJECT_ID);
    progress.projectViews = progress.viewedProjects.length;
    computeProgressPoints();
    tryUnlockBadges();
    saveProgressState();
    updateProfileWidgets();
  }
}

function recordCodeOpen() {
  progress.codeOpens += 1;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

function recordCompletion(projectId, projectTitle) {
  if (!projectId || projectIsCompleted(projectId)) return;

  progress.completedProjects.push({
    id: projectId,
    title: projectTitle || "Project " + projectId
  });

  progress.completions = progress.completedProjects.length;

  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();

  // Analyze portfolio after completion
  updatePortfolioAnalysis();
}
loadProgressState();
updatePortfolioAnalysis();
updateProfileWidgets();
async function updatePortfolioAnalysis() {

    const completedIds = progress.completedProjects.map(project => project.id);

    try {

        const response = await fetch("/api/portfolio-analysis", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                completed_projects: completedIds
            })
        });

        const result = await response.json();
        renderPortfolioAnalysis(result);

        // Exposed for debugging / other widgets that may want the raw data
        window.portfolioAnalysis = result;
    } catch (error) {

        console.error("Portfolio Analysis Error:", error);

    }
}
(function initIndexPage() {
  var form = document.getElementById("recommend-form");
  if (!form) return;

  var submitBtn = document.getElementById("submit-btn");
  var btnLabel = document.getElementById("btn-label");
  var btnLoading = document.getElementById("btn-loading");
  var resultsSection = document.getElementById("results-section");
  var resultsGrid = document.getElementById("results-grid");
  var showMoreBtn = document.getElementById("show-more-btn");
  var resultsLoadingEl = document.getElementById("results-loading");
  var resultsEmptyEl = document.getElementById("results-empty");
  var emptyMessageEl = document.getElementById("empty-message");
  var skillsHidden = document.getElementById("skills");
  var skillsInput = document.getElementById("skills-input");
  var selectedChips = document.getElementById("skill-chips-selected");
  var suggestions = document.getElementById("skills-suggestions");
  var skillWrap = document.getElementById("skill-input-wrap");
  var quickPickChips = Array.prototype.slice.call(document.querySelectorAll(".skill-chip"));
  var selectedSkills = [];
  var skillProficiencies = {};
  var availableSkills = (typeof skills !== "undefined" && Array.isArray(skills))
    ? skills.map(function (item) { return item.label; }).filter(Boolean)
    : quickPickChips.map(function (chip) { return chip.getAttribute("data-skill"); });
  var activeSuggestionIndex = -1;
  var visibleSuggestions = [];
  var hasSearched = false;
  var techStackSelect = document.getElementById("tech_stack");

  function normalize(value) {
    return String(value || "").trim().toLowerCase();
  }

  function syncSkillsHiddenInput() {
    skillsHidden.value = JSON.stringify(selectedSkills);
  }

  function isSelected(skill) {
    return selectedSkills.some(function (item) { return normalize(item) === normalize(skill); });
  }

  function canonicalSkill(rawSkill) {
    var trimmed = String(rawSkill || "").trim();
    var match = availableSkills.find(function (skill) { return normalize(skill) === normalize(trimmed); });
    return match || trimmed;
  }

  function updateQuickPickState() {
    quickPickChips.forEach(function (chip) {
      var active = isSelected(chip.getAttribute("data-skill"));
      chip.classList.toggle("active", active);
      chip.classList.toggle("selected", active);
      chip.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function renderSelectedChips() {
    selectedChips.textContent = "";
    selectedSkills.forEach(function (skill) {
      var chip = document.createElement("span");
      chip.className = "skill-chip-selected";
      chip.appendChild(document.createTextNode(skill + " (" + (skillProficiencies[skill] || "Beginner") + ")"));
      var button = document.createElement("button");
      button.type = "button";
      button.className = "skill-chip-remove";
      button.setAttribute("aria-label", "Remove " + skill);
      button.textContent = "x";
      button.addEventListener("click", function (event) {
        event.stopPropagation();
        removeSkill(skill);
      });
      chip.appendChild(button);
      selectedChips.appendChild(chip);
    });
  }

  window.addSkill = function addSkill(rawSkill) {
    var skill = canonicalSkill(rawSkill);
    if (!skill || isSelected(skill)) return;
    selectedSkills.push(skill);
    var proficiencySelect = document.getElementById("skill-proficiency");
    skillProficiencies[skill] = proficiencySelect ? proficiencySelect.value : "Beginner";
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    clearFieldError("skills-error");
    if (skillsInput) skillsInput.focus();
  };

  function removeSkill(skill) {
    selectedSkills = selectedSkills.filter(function (item) { return normalize(item) !== normalize(skill); });
    delete skillProficiencies[skill];
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
  }

  function clearFieldError(id) {
    var el = document.getElementById(id);
    if (el) el.textContent = "";
  }

  function showFieldError(id, message) {
    var el = document.getElementById(id);
    if (el) el.textContent = message;
  }

  function clearAllErrors() {
    ["skills-error", "level-error", "interest-error", "time-error"].forEach(clearFieldError);
    var general = document.getElementById("form-error-general");
    if (general) general.textContent = "";
  }

  function hideSuggestions() {
    visibleSuggestions = [];
    activeSuggestionIndex = -1;
    suggestions.style.display = "none";
    suggestions.textContent = "";
    skillsInput.setAttribute("aria-expanded", "false");
  }

  function filteredSkills(query) {
    var q = normalize(query);
    if (!q) return [];
    return availableSkills.filter(function (skill) {
      return normalize(skill).indexOf(q) !== -1 && !isSelected(skill);
    }).slice(0, 8);
  }

  function renderSuggestionState() {
    suggestions.querySelectorAll(".suggestion-item").forEach(function (item, index) {
      item.classList.toggle("suggestion-item--active", index === activeSuggestionIndex);
      item.setAttribute("aria-selected", index === activeSuggestionIndex ? "true" : "false");
    });
  }

  function showSuggestions(items) {
    visibleSuggestions = items;
    activeSuggestionIndex = -1;
    suggestions.textContent = "";
    if (!items.length) {
      hideSuggestions();
      return;
    }
    items.forEach(function (skill, index) {
      var item = document.createElement("div");
      item.className = "suggestion-item";
      item.id = "skills-suggestion-" + index;
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", "false");
      item.textContent = skill;
      item.addEventListener("mousedown", function (event) { event.preventDefault(); });
      item.addEventListener("mouseenter", function () {
        activeSuggestionIndex = index;
        renderSuggestionState();
      });
      item.addEventListener("click", function () {
        window.addSkill(skill);
        skillsInput.value = "";
        hideSuggestions();
      });
      suggestions.appendChild(item);
    });
    suggestions.style.display = "block";
    skillsInput.setAttribute("aria-expanded", "true");
  }

  function validateForm() {
    var valid = true;
    if (!selectedSkills.length) {
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

  function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.setAttribute("aria-busy", isLoading ? "true" : "false");
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline-flex" : "none";
    if (isLoading) {
      resultsSection.style.display = "block";
      resultsLoadingEl.style.display = "block";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "none";
      resultsGrid.innerHTML = "";
      resultsEmptyEl.style.display = "none";
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } else {
      resultsLoadingEl.style.display = "none";
    }
  }

  function truncate(text, maxLength) {
    text = text || "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

  function createTag(text, type) {
    var span = document.createElement("span");
    span.className = "project-tag project-tag--" + normalize(type).replace(/[^a-z0-9_-]/g, "-");
    span.textContent = text;
    return span;
  }

  function buildProjectCard(project) {
    var card = document.createElement("div");
    card.className = "project-card";

    if (project.match_score !== undefined) {
      var scoreBadge = document.createElement("div");
      scoreBadge.className = "project-match-score";
      scoreBadge.setAttribute("aria-label", "Match score: " + project.match_score + " out of 10");

      var scoreLabel = document.createElement("span");
      scoreLabel.className = "score-label";
      scoreLabel.textContent = "Match Score";

      var scoreValue = document.createElement("span");
      scoreValue.className = "score-value";
      scoreValue.textContent = project.match_score.toFixed(1) + " / 10";

      var scoreBar = document.createElement("div");
      scoreBar.className = "score-bar";
      scoreBar.setAttribute("role", "presentation");

      var scoreBarFill = document.createElement("div");
      scoreBarFill.className = "score-bar-fill";
      scoreBarFill.style.width = (project.match_score * 10) + "%";

      scoreBar.appendChild(scoreBarFill);
      scoreBadge.appendChild(scoreLabel);
      scoreBadge.appendChild(scoreValue);
      scoreBadge.appendChild(scoreBar);
      
      card.appendChild(scoreBadge);
    }

    if (project.match_explanation) {
      var explanationP = document.createElement("p");
      explanationP.className = "project-match-explanation";
      explanationP.innerHTML = '<svg class="explanation-icon" aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><span>' + project.match_explanation + '</span>';
      card.appendChild(explanationP);
    }

    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;

    var desc = document.createElement("p");
    desc.className = "project-card-desc";
    var descText = document.createElement("span");
    descText.className = "project-card-desc-text";
    descText.textContent = truncate(project.description, 120);
    desc.appendChild(descText);

    if (project.description && project.description.length > 120) {
      var expanded = false;
      var readMore = document.createElement("button");
      readMore.type = "button";
      readMore.className = "read-more-btn";
      readMore.setAttribute("aria-label", "Read full description for " + project.title);
      readMore.setAttribute("aria-expanded", "false");
      var readMoreLabel = document.createElement("span");
      readMoreLabel.textContent = "Read more";
      readMore.appendChild(readMoreLabel);
      readMore.addEventListener("click", function () {
        expanded = !expanded;
        descText.textContent = expanded ? project.description : truncate(project.description, 120);
        readMoreLabel.textContent = expanded ? "Read less" : "Read more";
        readMore.setAttribute("aria-expanded", expanded ? "true" : "false");
        readMore.setAttribute(
          "aria-label",
          (expanded ? "Collapse description for " : "Read full description for ") + project.title
        );
      });
      desc.appendChild(readMore);
    }

    var tags = document.createElement("div");
    tags.className = "project-card-tags";

    (project.skills || []).forEach(function (skill) { tags.appendChild(createTag(skill, "skill")); });
    tags.appendChild(createTag(project.level, project.level));
    tags.appendChild(createTag("Time: " + project.time, "time"));
    if (project.synergy_applied) {
      tags.appendChild(createTag("Synergy Match ✨", "synergy"));
    }

    var footer = document.createElement("div");
    footer.className = "project-card-footer";

    if (typeof DevPathBookmarks !== "undefined") {
      var saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.className = "btn-save-project";
      saveBtn.setAttribute("data-save-project-id", project.id);
      var isSaved = DevPathBookmarks.isSaved(project.id);
      if (isSaved) saveBtn.classList.add("saved");
      saveBtn.setAttribute("aria-pressed", isSaved ? "true" : "false");
      DevPathBookmarks.setButtonContent(saveBtn, isSaved);
      saveBtn.addEventListener("click", function () {
        DevPathBookmarks.toggle(project, saveBtn);
      });
      footer.appendChild(saveBtn);
    }

    var link = document.createElement("a");
    link.className = "btn-details";
    link.textContent = "View Full Project";
    link.href = "/project/" + project.id;
    footer.appendChild(link);

    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tags);

    card.appendChild(footer);
    return card;
  }

  var allProjects = [];
  var visibleProjectCount = 3;

  var PROJECTS_PER_LOAD = 3;

  function renderResults(projects, message) {
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    resultsGrid.innerHTML = "";
    if (!projects || projects.length === 0) {
      showMoreBtn.style.display = "none";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";
      if (emptyMessageEl) {
        emptyMessageEl.textContent = message || "Try adjusting your skills or choosing a different interest area.";
      }
      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }
    resultsEmptyEl.style.display = "none";
    resultsGrid.style.display = "grid";
    projects.forEach(function (project) { resultsGrid.appendChild(buildProjectCard(project)); });
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }
  if (showMoreBtn) {
      showMoreBtn.addEventListener("click", function () {
        visibleProjectCount += PROJECTS_PER_LOAD;
        
        renderResults(
          allProjects.slice(0, visibleProjectCount)
        );
        
        if (visibleProjectCount >= allProjects.length) {
          showMoreBtn.style.display = "none";
        }
      });
    }

  skillsInput.setAttribute("role", "combobox");
  skillsInput.setAttribute("aria-expanded", "false");
  suggestions.setAttribute("role", "listbox");

  skillsInput.addEventListener("input", function () {
    showSuggestions(filteredSkills(skillsInput.value));
  });
  skillsInput.addEventListener("focus", function () {
    if (skillsInput.value.trim()) showSuggestions(filteredSkills(skillsInput.value));
  });
  skillsInput.addEventListener("blur", function () {
    window.setTimeout(hideSuggestions, 150);
  });
  skillsInput.addEventListener("keydown", function (event) {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (!visibleSuggestions.length) showSuggestions(filteredSkills(skillsInput.value));
      if (!visibleSuggestions.length) return;
      event.preventDefault();
      activeSuggestionIndex = event.key === "ArrowDown"
        ? (activeSuggestionIndex + 1) % visibleSuggestions.length
        : (activeSuggestionIndex <= 0 ? visibleSuggestions.length - 1 : activeSuggestionIndex - 1);
      renderSuggestionState();
      return;
    }
    if (event.key === "Escape") {
      hideSuggestions();
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      if (activeSuggestionIndex >= 0 && visibleSuggestions[activeSuggestionIndex]) {
        window.addSkill(visibleSuggestions[activeSuggestionIndex]);
      } else {
        window.addSkill(skillsInput.value);
      }
      skillsInput.value = "";
      hideSuggestions();
    }
  });

  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");
      if (isSelected(skill)) removeSkill(skill);
      else window.addSkill(skill);
      skillsInput.value = "";
      hideSuggestions();
    });
  });

  if (skillWrap) {
    skillWrap.addEventListener("click", function () { skillsInput.focus(); });
  }

  // Toggle dropdown on button click
  var dropdownToggle = document.getElementById("skills-dropdown-toggle");
  if (dropdownToggle) {
    dropdownToggle.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var isExpanded = suggestions.style.display === "block";
      if (isExpanded) {
        hideSuggestions();
      } else {
        var unselectedSkills = availableSkills.filter(function (skill) {
          return !isSelected(skill);
        });
        showSuggestions(unselectedSkills);
      }
    });
  }

  function resetFormAndState() {
    form.reset();
    selectedSkills = [];
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    clearAllErrors();
    hideSuggestions();
    resultsSection.style.display = "none";
    showMoreBtn.style.display = "none";
    allProjects = [];
    visibleProjectCount = PROJECTS_PER_LOAD;
    if (skillsInput) skillsInput.focus();
  }

  var clearBtn = document.getElementById("clear-filters-btn");
  if (clearBtn) {
    clearBtn.addEventListener("click", resetFormAndState);
  }

  var inlineResetBtn = document.getElementById("reset-form-btn");
  if (inlineResetBtn) {
    inlineResetBtn.addEventListener("click", resetFormAndState);
  }

  var resetProgressBtn = document.getElementById("reset-progress-btn");
  if (resetProgressBtn) {
    resetProgressBtn.addEventListener("click", function () {
      progress.searches = 0;
      progress.projectViews = 0;
      progress.codeOpens = 0;
      progress.completions = 0;
      progress.points = 0;
      progress.viewedProjects = [];
      progress.completedProjects = [];
      progress.achievements = [];
      progress.badges = {
        first_search: false,
        project_explorer: false,
        code_starter: false,
        completionist: false,
        roadmap_runner: false
      };
      saveProgressState();
      updateProfileWidgets();
      showAchievementToast("Progress reset", "Your local profile has been cleared.");
    });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearAllErrors();
    if (skillsInput.value.trim()) {
      window.addSkill(skillsInput.value);
      skillsInput.value = "";
      hideSuggestions();
    }
    if (!validateForm()) return;
    setLoadingState(true);
    fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        skills: JSON.stringify(selectedSkills.map(function (skill) {
          return {
            skill: skill,
            proficiency: skillProficiencies[skill] || "Beginner"
          };
        })),
        level: document.getElementById("level").value,
        interest: document.getElementById("interest").value,
        time: document.getElementById("time").value,
        tech_stack: techStackSelect ? techStackSelect.value : "all"
      })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error(data.error || "Unable to generate recommendations.");
          return data;
        });
      })
      .then(function (data) {
        setLoadingState(false);
        recordSearch();
        hasSearched = true;

        allProjects = data.projects || [];
        visibleProjectCount = PROJECTS_PER_LOAD;

        renderResults(
          allProjects.slice(0, visibleProjectCount),data.message);
  
        if (allProjects.length > visibleProjectCount) {
          showMoreBtn.style.display = "inline-block";
        } else {
          showMoreBtn.style.display = "none";
        }

         // Update URL query parameters so the result is shareable
        try {
          var params = new URLSearchParams();
          params.set("skills", JSON.stringify(selectedSkills));
          params.set("level", document.getElementById("level").value);
          params.set("interest", document.getElementById("interest").value);
          params.set("time", document.getElementById("time").value);
          window.history.replaceState(null, "", "?" + params.toString());
      } catch (e) {}
      })
      .catch(function (err) {
        setLoadingState(false);
        var general = document.getElementById("form-error-general");
        if (general) general.textContent = err.message || "An unexpected error occurred. Please try again.";
      });
  });

  if (techStackSelect) {
    techStackSelect.addEventListener("change", function () {
      if (hasSearched) {
        submitBtn.click();
      }
    });
  }

  var modal = document.getElementById("github-modal-overlay");
  var openModalBtn = document.getElementById("btn-show-github");
  var closeModalBtn = document.getElementById("btn-close-github");
  var errorMsg = document.getElementById("github-modal-error");

  function closeGithubModal() {
    modal.classList.remove("active");
    if (errorMsg) errorMsg.textContent = "";
  }

  if (modal && openModalBtn && closeModalBtn && errorMsg) {
    openModalBtn.addEventListener("click", function () {
      modal.classList.add("active");
    });
    closeModalBtn.addEventListener("click", closeGithubModal);
    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeGithubModal();
    });
  }

  // Handle OAuth callback logic
  var urlParams = new URLSearchParams(window.location.search);
  var githubAuth = urlParams.get("github_auth");
  
  if (githubAuth === "success") {
    // Optional: show some loading UI here if desired
    fetch("/api/github/repos")
      .then(function (response) {
        if (!response.ok) throw new Error("Unable to fetch GitHub repositories.");
        return response.json();
      })
      .then(function (repos) {
        var languages = [];
        repos.forEach(function (repo) {
          if (repo.language && languages.indexOf(repo.language) === -1) languages.push(repo.language);
        });
        if (!languages.length) {
          if (modal && errorMsg) {
            modal.classList.add("active");
            errorMsg.textContent = "No public languages found in your GitHub repositories.";
          }
          return;
        }
        languages.forEach(window.addSkill);
        window.history.replaceState({}, document.title, window.location.pathname);
      })
      .catch(function (err) {
        if (modal && errorMsg) {
          modal.classList.add("active");
          errorMsg.textContent = err.message || "Failed to fetch skills.";
        }
        window.history.replaceState({}, document.title, window.location.pathname);
      });
  } else if (githubAuth === "error") {
    if (modal && errorMsg) {
      modal.classList.add("active");
      errorMsg.textContent = "GitHub authentication failed. Please try again.";
    }
    window.history.replaceState({}, document.title, window.location.pathname);
  }
})();

(function initDetailPage() {
  if (typeof PROJECT_ID === "undefined") return;
  recordProjectView();

  var codePanel = document.getElementById("code-panel");
  var codePanelOverlay = document.getElementById("code-panel-overlay");
  var codeContentEl = document.getElementById("code-content");
  var codePanelFilename = document.getElementById("code-panel-filename");
  var btnViewCode = document.getElementById("btn-view-code");
  var btnViewCodeSm = document.getElementById("btn-view-code-sm");
  var btnClosePanel = document.getElementById("code-panel-close");
  var btnCopyCode = document.getElementById("btn-copy-code");
  var copyToast = document.getElementById("copy-toast");
  var completionBtn = document.getElementById("btn-mark-complete");
  var codeFetched = false;

  function renderCode(code) {
    codeContentEl.textContent = "";
    String(code || "").split("\n").forEach(function (line, index) {
      var row = document.createElement("div");
      row.className = "code-line";
      var number = document.createElement("span");
      number.className = "line-number";
      number.setAttribute("aria-hidden", "true");
      number.textContent = index + 1;
      var content = document.createElement("span");
      content.className = "line-content";
      content.textContent = line;
      row.appendChild(number);
      row.appendChild(content);
      codeContentEl.appendChild(row);
    });
  }

  function fetchStarterCode() {
    codeContentEl.textContent = "Loading starter code...";
    fetch("/project/" + PROJECT_ID + "/code")
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error(data.error || "Starter code unavailable.");
          return data;
        });
      })
      .then(function (data) {
        codePanelFilename.textContent = data.filename;
        renderCode(data.code);
        codeFetched = true;
      })
      .catch(function (err) {
        codeContentEl.textContent = err.message || "Could not load starter code. Try downloading it instead.";
      });
  }

  function openCodePanel() {
    if (!codePanel) return;
    codePanel.classList.add("active");
    if (codePanelOverlay) codePanelOverlay.classList.add("active");
    document.body.style.overflow = "hidden";
    recordCodeOpen();
    if (!codeFetched) fetchStarterCode();
  }

  function closeCodePanel() {
    if (!codePanel) return;
    codePanel.classList.remove("active");
    if (codePanelOverlay) codePanelOverlay.classList.remove("active");
    document.body.style.overflow = "";
  }

  if (btnViewCode) btnViewCode.addEventListener("click", openCodePanel);
  if (btnViewCodeSm) btnViewCodeSm.addEventListener("click", openCodePanel);
  if (btnClosePanel) btnClosePanel.addEventListener("click", closeCodePanel);
  if (codePanelOverlay) codePanelOverlay.addEventListener("click", closeCodePanel);
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeCodePanel();
  });

  if (btnCopyCode) {
    btnCopyCode.addEventListener("click", function () {
      var code = Array.prototype.slice.call(codeContentEl.querySelectorAll(".line-content"))
        .map(function (line) { return line.textContent; })
        .join("\n");
      if (!code) return;
      var done = function () {
        if (copyToast) {
          copyToast.classList.add("show");
          window.setTimeout(function () { copyToast.classList.remove("show"); }, 2500);
        }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(done);
      } else {
        var textarea = document.createElement("textarea");
        textarea.value = code;
        textarea.style.cssText = "position:fixed;top:-9999px;left:-9999px";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        try { document.execCommand("copy"); } catch (err) {}
        document.body.removeChild(textarea);
        done();
      }
    });
  }

  var roadmapCheckboxes = Array.prototype.slice.call(document.querySelectorAll(".roadmap-checkbox"));
  var progressFill = document.getElementById("roadmap-progress-fill");
  var progressText = document.getElementById("roadmap-progress-text");
  var progressBar = document.querySelector(".roadmap-progress-bar");
  var roadmapStorageKey = "devpath-roadmap-progress-" + (typeof PROJECT_ID !== 'undefined' ? PROJECT_ID : "");

  function updateRoadmapProgress(skipSave) {
    if (!roadmapCheckboxes.length) return;
    var completedCount = roadmapCheckboxes.filter(function (checkbox) { return checkbox.checked; }).length;
    var percent = Math.round((completedCount / roadmapCheckboxes.length) * 100);
    roadmapCheckboxes.forEach(function (checkbox) {
      var step = checkbox.closest(".roadmap-step");
      if (step) step.classList.toggle("completed", checkbox.checked);
    });
    
    if (progressFill) progressFill.style.width = percent + "%";
    if (progressText) progressText.textContent = percent + "% completed";
    if (progressBar) progressBar.setAttribute("aria-valuenow", String(percent));
    // Disable completion button unless all steps are completed
    var completionBtn = document.getElementById("btn-mark-complete");
    if (completionBtn && typeof PROJECT_ID !== "undefined") {
      var isAlreadyCompleted = projectIsCompleted(PROJECT_ID);
      if (isAlreadyCompleted) {
        completionBtn.textContent = "Project Completed";
        completionBtn.disabled = true;
      } else {
        var allChecked = completedCount === roadmapCheckboxes.length;
        if (allChecked) {
          completionBtn.textContent = "Mark Project Complete";
          completionBtn.disabled = false;
        } else {
          completionBtn.textContent = "Complete All Steps First";
          completionBtn.disabled = true;
        }
      }
    }

    if (skipSave === true) return;

    var completedStates = roadmapCheckboxes.map(function (checkbox) {
      return checkbox.checked;
    });

    if (typeof USER_LOGGED_IN !== 'undefined' && USER_LOGGED_IN) {
      fetch("/api/project/" + PROJECT_ID + "/progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed_steps: completedStates })
      }).catch(console.error);
    } else {
      try {
        localStorage.setItem(roadmapStorageKey, JSON.stringify(completedStates));
      } catch (err) {}
    }
  }

  function renderRoadmapFromState(saved) {
    roadmapCheckboxes.forEach(function (checkbox, index) {
      checkbox.checked = !!saved[index];
    });
    updateRoadmapProgress(true);
  }

  if (roadmapCheckboxes.length > 0) {
    if (typeof USER_LOGGED_IN !== 'undefined' && USER_LOGGED_IN) {
      fetch("/api/project/" + PROJECT_ID + "/progress")
        .then(function(res) { return res.json(); })
        .then(function(data) { renderRoadmapFromState(data.completed_steps || []); })
        .catch(console.error);
    } else {
      try {
        var saved = JSON.parse(localStorage.getItem(roadmapStorageKey) || "[]");
        renderRoadmapFromState(saved);
      } catch (err) {}
    }

    roadmapCheckboxes.forEach(function (checkbox) {
      checkbox.addEventListener("change", function() { updateRoadmapProgress(false); });
    });
  }

  // Initialize expandable roadmap details
  var stepToggles = document.querySelectorAll(".btn-step-details-toggle");
  var stepTexts = document.querySelectorAll(".roadmap-step-text");
  var stepGuidances = document.querySelectorAll(".step-detailed-guidance");

  var guidanceRules = [
    { pattern: /set\s*up|folder|create|initialize/i, text: "Initialize your project workspace. Create a dedicated directory, initialize Git version control, and set up your configuration or main script files (e.g., main.py, index.html). Plan your module structure." },
    { pattern: /design|structure|database|schema|model/i, text: "Determine the data entities and attributes. Write down the schema or dictionary layout, choose key-value pairs, and decide on database or memory storage mechanism." },
    { pattern: /function|logic|write|implement|calculate|process/i, text: "Draft helper functions with clear inputs and outputs. Focus on clean implementation of core business logic first, keeping functions modular, clean, and testable." },
    { pattern: /api|fetch|endpoint|route|request|http/i, text: "Implement routes/controllers for handling HTTP requests. Verify correct status codes, JSON formats, and integrate error handling for network or request failures." },
    { pattern: /ui|interface|frontend|view|css|style|render|display/i, text: "Build a responsive interface using semantic HTML and clean styling. Design for mobile-first views and verify interactive component states (hover, focus, disabled)." },
    { pattern: /test|bug|mock|assert|verify/i, text: "Write test cases (unit/integration) or manually test inputs to verify the code handles edge cases, empty values, and invalid format errors gracefully." }
  ];

  function getGuidanceText(stepText) {
    for (var i = 0; i < guidanceRules.length; i++) {
      if (guidanceRules[i].pattern.test(stepText)) {
        return guidanceRules[i].text;
      }
    }
    return "Break down this milestone into smaller tasks. Research best libraries or methods, implement a prototype, and review for performance and correctness.";
  }

  stepTexts.forEach(function (el, index) {
    if (stepGuidances[index]) {
      stepGuidances[index].textContent = getGuidanceText(el.textContent);
    }
  });

  stepToggles.forEach(function (btn, index) {
    btn.addEventListener("click", function (event) {
      event.preventDefault();
      var guidance = stepGuidances[index];
      if (!guidance) return;
      var isHidden = guidance.style.display === "none";
      guidance.style.display = isHidden ? "block" : "none";
      var label = btn.querySelector("span");
      if (label) label.textContent = isHidden ? "Hide Details" : "Show Details";
      var chevron = btn.querySelector(".chevron-icon");
      if (chevron) {
        chevron.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
      }
    });
  });

  if (completionBtn) {
    completionBtn.addEventListener("click", function () {
      recordCompletion(PROJECT_ID, typeof PROJECT_TITLE !== "undefined" ? PROJECT_TITLE : "");
      showAchievementToast("Project completed", "Nice work finishing this project.");
    });
  }

  // Handle shareable results URL via query parameters
  function parseUrlQueryParams() {
    var params = new URLSearchParams(window.location.search);
    var skillsParam = params.get("skills");
    var levelParam = params.get("level");
    var interestParam = params.get("interest");
    var timeParam = params.get("time");

    var hasParams = false;

    if (skillsParam) {
      hasParams = true;
      try {
        var parsed = JSON.parse(skillsParam);
        if (Array.isArray(parsed)) {
          parsed.forEach(function (skill) {
            window.addSkill(skill);
          });
        } else if (typeof parsed === "string") {
          parsed.split(",").forEach(function (skill) {
            window.addSkill(skill.trim());
          });
        }
      } catch (e) {
        skillsParam.split(",").forEach(function (skill) {
          window.addSkill(skill.trim());
        });
      }
    }

    if (levelParam) {
      hasParams = true;
      var levelEl = document.getElementById("level");
      if (levelEl) levelEl.value = levelParam;
    }

    if (interestParam) {
      hasParams = true;
      var interestEl = document.getElementById("interest");
      if (interestEl) interestEl.value = interestParam;
    }

    if (timeParam) {
      hasParams = true;
      var timeEl = document.getElementById("time");
      if (timeEl) timeEl.value = timeParam;
    }

    if (hasParams && form) {
      setTimeout(function () {
        form.dispatchEvent(new Event("submit"));
      }, 100);
    }
  }

  if (form) {
    parseUrlQueryParams();
  }
})();

(function initScrollButton() {
  var button = document.getElementById("scroll-top-btn");
  var icon = document.getElementById("scroll-btn-icon");
  if (!button) return;
  var atBottom = false;

  function nearBottom() {
    return window.innerHeight + window.pageYOffset >= document.body.scrollHeight - 40;
  }

  function update() {
    button.classList.toggle("visible", window.pageYOffset > 200);
    atBottom = nearBottom();
    button.setAttribute("aria-label", atBottom ? "Scroll to top" : "Scroll to bottom");
    button.title = atBottom ? "Scroll to top" : "Scroll to bottom";
    if (icon) icon.innerHTML = atBottom ? '<polyline points="18 15 12 9 6 15"/>' : '<polyline points="6 9 12 15 18 9"/>';
  }

  window.addEventListener("scroll", update, { passive: true });
  button.addEventListener("click", function () {
    window.scrollTo({ top: atBottom ? 0 : document.body.scrollHeight, behavior: "smooth" });
  });
  update();
})();
function renderPortfolioAnalysis(result) {

  var container = document.getElementById("portfolio-analysis-container");
  if (!container) return;

  var hasCompleted = progress.completedProjects && progress.completedProjects.length > 0;

  if (!hasCompleted) {
    container.innerHTML =
      '<div class="portfolio-card portfolio-card--empty">' +
        '<div class="portfolio-empty-icon">📊</div>' +
        '<h3>No completed projects yet</h3>' +
        '<p>Mark a project complete from its project page and your portfolio diversity score will show up here.</p>' +
      '</div>';
    return;
  }

  var score = typeof result.score === "number" ? result.score : 0;
  var scoreTier =
    score >= 80 ? "excellent" :
    score >= 50 ? "good" : "low";

  var scoreLabel =
    score >= 80 ? "Well-rounded portfolio" :
    score >= 50 ? "Good progress, room to grow" :
    "Let's diversify your portfolio";

  var categories = Array.isArray(result.categories) ? result.categories : [];
  var recommendations = Array.isArray(result.recommendations) ? result.recommendations : [];

  var categoryCards = categories.map(function (cat) {
    var stateClass = cat.covered ? "is-covered" : "is-missing";
    var statusIcon = cat.covered
      ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
      : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

    return (
      '<div class="portfolio-cat-card ' + stateClass + '">' +
        '<span class="portfolio-cat-icon">' + cat.icon + '</span>' +
        '<span class="portfolio-cat-name">' + cat.name + '</span>' +
        '<span class="portfolio-cat-status">' + statusIcon + '</span>' +
      '</div>'
    );
  }).join("");

  var recommendationCards = recommendations.length
    ? recommendations.map(function (rec) {
        return (
          '<div class="portfolio-rec-card">' +
            '<span class="portfolio-rec-icon">' + rec.icon + '</span>' +
            '<div class="portfolio-rec-text">' +
              '<span class="portfolio-rec-category">' + rec.category + '</span>' +
              '<span class="portfolio-rec-title">' + rec.title + '</span>' +
            '</div>' +
          '</div>'
        );
      }).join("")
    : '<p class="portfolio-rec-empty">You\u2019ve covered every domain we track. Amazing work!</p>';

  container.innerHTML =
    '<div class="portfolio-card">' +
      '<div class="portfolio-summary">' +
        '<div class="portfolio-gauge portfolio-gauge--' + scoreTier + '" style="--score:' + score + ';">' +
          '<div class="portfolio-gauge-inner">' +
            '<span class="portfolio-gauge-value">' + score + '</span>' +
            '<span class="portfolio-gauge-max">/ 100</span>' +
          '</div>' +
        '</div>' +
        '<div class="portfolio-summary-text">' +
          '<span class="portfolio-summary-eyebrow">Diversity Score</span>' +
          '<h3>' + scoreLabel + '</h3>' +
          '<p>' + (result.covered_count != null ? result.covered_count : categories.filter(function(c){return c.covered;}).length) +
            ' of ' + (result.total_categories || categories.length) +
            ' skill domains covered across your completed projects.</p>' +
        '</div>' +
      '</div>' +

      '<div class="portfolio-cat-grid">' + categoryCards + '</div>' +

      '<div class="portfolio-recommendations">' +
        '<h4>🚀 Recommended Next Projects</h4>' +
        '<div class="portfolio-rec-grid">' + recommendationCards + '</div>' +
      '</div>' +
    '</div>';
}