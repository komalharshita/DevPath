<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description"
    content="DevPath recommends real coding projects based on your skills, level, and interests — with full roadmaps and starter code." />
  <title>DevPath — Find Projects Based On Your Skills</title>
  
  <!-- Open Graph meta tags for social media sharing -->
  <meta property="og:title" content="DevPath — Find Projects Based On Your Skills" />
  <meta property="og:description" content="{{ config.SITE_DESCRIPTION }}" />
  <meta property="og:image" content="{{ config.get_og_image_url() }}" />
  <meta property="og:url" content="{{ config.get_base_url() }}/" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="{{ config.SITE_NAME }}" />
  
  <!-- Twitter Card meta tags -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="DevPath — Find Projects Based On Your Skills" />
  <meta name="twitter:description" content="{{ config.SITE_DESCRIPTION }}" />
  <meta name="twitter:image" content="{{ config.get_og_image_url() }}" />
  
  <script>
    document.documentElement.setAttribute("data-entry-anim", "true");
  </script>
  <link rel="icon" href="/static/favicon.svg" type="image/svg+xml" />
  {% include 'partials/theme_head.html' %}
  <link rel="stylesheet" href="/static/style.css" />
  <link
    href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap"
    rel="stylesheet" />
  
  <style>
    /* ============================================
       REDESIGNED PROFILE SECTION STYLES
       Only these styles are new - rest remain original
       ============================================ */
    
    /* Stats Dashboard Grid */
    .stats-dashboard-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .stat-dashboard-card {
      background: var(--card-bg, #ffffff);
      border-radius: 1.25rem;
      padding: 1.25rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      border: 1px solid var(--border, #e5e7eb);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stat-dashboard-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 24px -12px rgba(0,0,0,0.15);
    }

    .stat-dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .stat-dashboard-title {
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted, #6b7280);
    }

    .stat-dashboard-value {
      font-size: 2.5rem;
      font-weight: 800;
      margin-bottom: 0.75rem;
      background: linear-gradient(135deg, #6366f1, #8b5cf6);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }

    .stat-dashboard-progress {
      margin: 0.75rem 0;
    }

    .progress-meter {
      background: var(--gray-200, #e5e7eb);
      border-radius: 100px;
      height: 8px;
      overflow: hidden;
// script.js — DevPath client-side logic
//
// Responsibilities:
//   - Mobile navigation toggle
//   - Skill chip manager (add/remove skills)
//   - Form validation with per-field error messages
//   - Recommendation API call and loading states
//   - Result card rendering
//   - Code viewer panel (detail page)
// DevPath client-side behavior.

// ============================================================
// THEME PREVIEW MODAL & TOGGLE
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
  // Inject the theme modal HTML
  var modalHtml = `
<div id="theme-preview-modal" class="theme-modal-overlay" aria-hidden="true" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:10000; backdrop-filter:blur(4px); align-items:center; justify-content:center;">
  <div class="theme-modal-content" role="dialog" aria-modal="true" aria-labelledby="theme-modal-title" style="background:var(--surface); border:1px solid var(--border); border-radius:var(--r-lg); padding:1.5rem; max-width:500px; width:90%; box-shadow:var(--shadow-xl);">
    <div class="theme-modal-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
      <h2 id="theme-modal-title" style="font-size:1.25rem; margin:0; color:var(--text-heading);">Choose a Theme</h2>
      <button id="close-theme-modal" class="btn-clear" aria-label="Close modal" style="background:transparent; border:none; font-size:1.5rem; cursor:pointer; color:var(--text-light);">&times;</button>
    </div>
    <div class="theme-preview-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
      <!-- Light Theme Card -->
      <button class="theme-preview-card" data-theme-target="light" style="background:transparent; border:2px solid var(--border); border-radius:var(--r-md); padding:1rem; cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:1rem; transition:all 0.2s ease;">
        <div class="preview-mockup" style="width:100%; background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:8px; display:flex; flex-direction:column; gap:6px;">
          <div style="width:100%; height:12px; background:#f1f5f9; border-radius:3px;"></div>
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
  var html = document.documentElement;

  function syncTheme(theme) {
    html.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch (e) {}
    
    // Sync accessibility attributes on toggle buttons
    var isDark = theme === "dark";
    document.querySelectorAll(".theme-toggle").forEach(function(btn) {
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    });

    // Update active card styles
    cards.forEach(function(card) {
      if (card.getAttribute("data-theme-target") === theme) {
        card.style.borderColor = "var(--accent)";
      } else {
        card.style.borderColor = "var(--border)";
      }
    });
  }

  // Set initial theme in UI
  var activeTheme = html.getAttribute("data-theme") || localStorage.getItem("theme") || "light";
  syncTheme(activeTheme);

  // Toggle modal on theme button click
  document.querySelectorAll(".theme-toggle").forEach(function(btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    });
  });

  // Close modal
  function closeModal() {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
  }

  closeBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", function(e) {
    if (e.target === modal) closeModal();
  });

  // Apply theme when card is clicked
  cards.forEach(function(card) {
    card.addEventListener("click", function() {
      var theme = this.getAttribute("data-theme-target");
      syncTheme(theme);
      setTimeout(closeModal, 150); // slight delay for visual feedback
    });
    card.addEventListener("mouseenter", function() {
      if (this.getAttribute("data-theme-target") !== html.getAttribute("data-theme")) {
        this.style.borderColor = "var(--gray-400)";
      }
    });
    card.addEventListener("mouseleave", function() {
      if (this.getAttribute("data-theme-target") !== html.getAttribute("data-theme")) {
        this.style.borderColor = "var(--border)";
      }
    });
  });
});

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

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest(".theme-toggle");
    if (!toggle) return;
    event.preventDefault();
    var current = html.getAttribute("data-theme") || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  });

  initTheme();
})();

(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu = document.getElementById("nav-mobile-menu");
  if (!toggle || !menu) return;

  toggle.addEventListener("click", function () {
    var isOpen = menu.classList.toggle("open");
    toggle.classList.toggle("open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen);
  });

  document.querySelectorAll(".nav-mobile-link").forEach(function (link) {
    link.addEventListener("click", function () {
      menu.classList.remove("open");
      toggle.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
})();

  function setOpen(isOpen) {
    menu.classList.toggle("open", isOpen);
    toggle.classList.toggle("open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
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
    meterFill.textContent = percentage + "%";
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
    completionBtn.textContent = completed ? "Project Completed" : "Mark Project Complete";
    completionBtn.disabled = completed;
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
  progress.completedProjects.push({ id: projectId, title: projectTitle || "Project " + projectId });
  progress.completions = progress.completedProjects.length;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

loadProgressState();
updateProfileWidgets();

// ============================================================
// INDEX PAGE
// ============================================================
(function initIndexPage() {
  var form = document.getElementById("recommend-form");
  if (!form) return;

  var submitBtn = document.getElementById("submit-btn");
  var btnLabel = document.getElementById("btn-label");
  var btnLoading = document.getElementById("btn-loading");
  var resultsSection = document.getElementById("results-section");
  var resultsGrid = document.getElementById("results-grid");
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
  var availableSkills = (typeof skills !== "undefined" && Array.isArray(skills))
    ? skills.map(function (item) { return item.label; }).filter(Boolean)
    : quickPickChips.map(function (chip) { return chip.getAttribute("data-skill"); });
  var activeSuggestionIndex = -1;
  var visibleSuggestions = [];
  var SAVED_PROJECTS_KEY = "devpathSavedProjects";
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

  // Add skill on Enter key in the text input
  // we intercept Enter here so it doesn't accidentally submit the whole form
  skillsTextInput.addEventListener("keydown", function (evt) {
    if (evt.key === "ArrowDown" || evt.key === "ArrowUp") {
      if (visibleSuggestions.length === 0) displaySuggestions(getFilteredSkills(skillsTextInput.value));
      if (visibleSuggestions.length === 0) return;
      evt.preventDefault();
      if (evt.key === "ArrowDown") {
        activeSuggestionIndex = (activeSuggestionIndex + 1) % visibleSuggestions.length;
      } else {
        activeSuggestionIndex = activeSuggestionIndex <= 0 ? visibleSuggestions.length - 1 : activeSuggestionIndex - 1;
      }
      renderActiveSuggestion();
      return;
    }
    if (evt.key === "Escape") { hideSuggestions(); return; }
    if (evt.key === "Enter") {
      evt.preventDefault();
      if (activeSuggestionIndex >= 0 && visibleSuggestions[activeSuggestionIndex]) {
        selectSuggestion(visibleSuggestions[activeSuggestionIndex]);
        return;
      }
      if (skillsTextInput.value.trim()) { addSkill(skillsTextInput.value); skillsTextInput.value = ""; }
      hideSuggestions();
    }
  });

    .progress-meter-fill {
      background: linear-gradient(90deg, #6366f1, #8b5cf6);
      height: 100%;
      border-radius: 100px;
      display: block;
      width: 0%;
      transition: width 0.3s ease;
    }

    .stat-dashboard-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.7rem;
      color: var(--text-muted, #6b7280);
      margin-top: 0.75rem;
    }

    .reset-btn-mini {
      background: none;
      border: none;
      color: var(--text-muted, #6b7280);
      font-size: 0.7rem;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      border-radius: 0.5rem;
      transition: all 0.2s;
    }

    .reset-btn-mini:hover {
      background: var(--gray-100, #f3f4f6);
      color: #ef4444;
    }

    /* Badges Grid Mini */
    .badges-grid-mini {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin: 0.75rem 0;
      min-height: 60px;
    }

    .badge-mini {
      background: var(--gray-100, #f3f4f6);
      padding: 0.4rem 0.75rem;
      border-radius: 2rem;
      font-size: 0.7rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }

    .badge-mini.earned {
      background: linear-gradient(135deg, #fbbf24, #f59e0b);
      color: white;
  // Add/toggle skill on quick-pick chip click
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");
      if (!skill) return;
      if (isSkillSelected(skill)) { removeSkill(skill); } else { addSkill(skill); }
      skillsTextInput.value = "";
      hideSuggestions();
  function renderSelectedChips() {
    selectedChips.textContent = "";
    selectedSkills.forEach(function (skill) {
      var chip = document.createElement("span");
      chip.className = "skill-chip-selected";
      chip.appendChild(document.createTextNode(skill));
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
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    clearFieldError("skills-error");
    if (skillsInput) skillsInput.focus();
  };

  function removeSkill(skill) {
    selectedSkills = selectedSkills.filter(function (item) { return normalize(item) !== normalize(skill); });
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

  // checks form fields and shows error messages if any required field is missing or invalid. 
  // Returns true if the form is valid, false otherwise
  function validateForm() {
    var valid = true;

    // Check both the array and the hidden input since skills can come from either source
    if (selectedSkills.length === 0 && !skillsHidden.value.trim()) {
      showFieldError("skills-error", "Please add at least one skill.");
      valid = false;
    }

    /* Activity Stats */
    .activity-stats-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-top: 0.5rem;
    }

    .activity-stat-item {
      text-align: center;
      padding: 0.75rem;
      background: var(--gray-50, #f9fafb);
      border-radius: 1rem;
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

  // Multi-select dropdown toggle functionality
  var dropdownBtn = document.getElementById("skills-dropdown-toggle");
  if (dropdownBtn) {
    dropdownBtn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var suggestionsOpen = suggestionsDiv.style.display === "block";
      
      if (suggestionsOpen) {
        hideSuggestions();
      } else {
        // Show all available skills in dropdown
        displaySuggestions(availableSkills);
        suggestionsDiv.classList.add("show");
      }
    });
  }

  // Show suggestions on input
  skillsTextInput.addEventListener("input", function (evt) {
    var typedValue = evt.target.value.trim();
    if (typedValue.length === 0) {
      hideSuggestions();
      return;
    if (!document.getElementById("interest").value) {
      showFieldError("interest-error", "Please select an area of interest.");
      valid = false;
    }

    .activity-stat-value {
      display: block;
      font-size: 1.5rem;
      font-weight: 700;
      color: #6366f1;
    }

    return valid;
  }

    .activity-stat-label {
      font-size: 0.7rem;
      color: var(--text-muted, #6b7280);
    }

    /* Bottom Grid */
    .profile-bottom-grid {
      display: grid;
      grid-template-columns: 1fr 1.2fr;
      gap: 1.5rem;
    }

    .completed-card,
    .leaderboard-achievement-card {
      background: var(--card-bg, #ffffff);
      border-radius: 1.25rem;
      padding: 1.25rem;
      border: 1px solid var(--border, #e5e7eb);
    }

    .completed-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border, #e5e7eb);
    }

    .completed-header h3 {
      font-size: 1rem;
      font-weight: 600;
      margin: 0;
    }

    .empty-completed {
      text-align: center;
      padding: 2rem;
      color: var(--text-muted, #6b7280);
    }

    .empty-completed svg {
      margin-bottom: 0.75rem;
      opacity: 0.5;
    }

    .empty-completed p {
      margin: 0;
      font-weight: 500;
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
      var skillsHidden = document.getElementById("skills");
    }
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

  // ----------------------------------------------------------
  // Loading state
  // ----------------------------------------------------------

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
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } else {
      resultsLoadingEl.style.display = "none";
    }
  }

  // ----------------------------------------------------------
  // Render result cards
  // ----------------------------------------------------------

  //takes the array of projects from the api and draws them on the page as cards
  //if array is empty it shows the "no results" message instead
  // Renders project result cards or shows the empty-state message.
  function renderResults(projects, message) {
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    resultsGrid.innerHTML = "";

    var shareWrap = document.getElementById("share-result-wrap");
    var hasResults = projects && projects.length > 0;

    // Single consolidated toggle for empty vs. populated state
    resultsGrid.style.display    = hasResults ? "grid" : "none";
    resultsEmptyEl.style.display = hasResults ? "none" : "block";
    if (shareWrap) shareWrap.style.display = hasResults ? "flex" : "none";

    if (!hasResults) {
      var displayMsg = message || "Try adjusting your skills or selecting a different interest area.";
      if (emptyMessageEl) {
        emptyMessageEl.textContent = displayMsg;
      }
      resultsEmptyEl.innerHTML = 
        '<div class="empty-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; max-width: 560px; margin: 0 auto; padding: 40px 20px; border: 1.5px dashed var(--border); border-radius: var(--r-md); background: var(--card-bg, #ffffff);">' +
          '<div class="empty-icon" style="color: var(--gray-400); margin-bottom: 16px;">' +
            '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
              '<circle cx="12" cy="12" r="10" />' +
              '<line x1="12" y1="8" x2="12" y2="12" />' +
              '<line x1="12" y1="16" x2="12.01" y2="16" />' +
            '</svg>' +
          '</div>' +
          '<h3 style="font-family: var(--font-display); font-size: 1.3rem; font-weight: 700; color: var(--text-heading); margin-bottom: 12px;">We couldn\'t find an exact match for your current filters.</h3>' +
          '<p id="empty-message" style="color: var(--text-body); font-size: 0.95rem; margin-bottom: 24px; max-width: 440px; line-height: 1.5;">' + displayMsg + '</p>' +
          '<div class="empty-relaxation-tips" style="background: var(--surface-light, #f9fafb); border: 1px solid var(--border); border-radius: var(--r-sm); padding: 16px 20px; margin-bottom: 24px; text-align: left; width: 100%; max-width: 440px;">' +
            '<span style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); display: block; margin-bottom: 10px;">Try relaxing your search constraints:</span>' +
            '<ul style="list-style: none; padding: 0; margin: 0; font-size: 0.88rem; color: var(--text-body); display: flex; flex-direction: column; gap: 8px;">' +
              '<li style="display: flex; gap: 8px; align-items: flex-start;">' +
                '<span style="color: var(--indigo-500); font-weight: bold;">•</span>' +
                '<span>Choose <strong>All Technologies</strong> in the Tech Stack dropdown selector.</span>' +
              '</li>' +
              '<li style="display: flex; gap: 8px; align-items: flex-start;">' +
                '<span style="color: var(--indigo-500); font-weight: bold;">•</span>' +
                '<span>Clear some of your selected skills to broaden recommendations.</span>' +
              '</li>' +
              '<li style="display: flex; gap: 8px; align-items: flex-start;">' +
                '<span style="color: var(--indigo-500); font-weight: bold;">•</span>' +
                '<span>Select a different Area of Interest or increase your Time Availability.</span>' +
              '</li>' +
            '</ul>' +
          '</div>' +
          '<button id="empty-state-reset-btn" class="btn-try-again" type="button" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 11px 24px;">' +
            'Clear All Filters' +
          '</button>' +
        '</div>';

      var resetBtn = document.getElementById("empty-state-reset-btn");
      if (resetBtn) {
        resetBtn.addEventListener("click", function () {
          var mainClearBtn = document.getElementById("clear-filters-btn");
          if (mainClearBtn) {
            mainClearBtn.click();
          }
        });
      }

      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    recordSearch();
    // Build a card for each project and add it to the grid
    projects.forEach(function (project) {
      resultsGrid.appendChild(buildProjectCard(project));
    });

    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

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
    descText.textContent = truncate(project.description, 120);
    desc.appendChild(descText);

    if (project.description && project.description.length > 120) {
      var expanded = false;
      var readMore = document.createElement("button");
      readMore.type = "button";
      readMore.className = "read-more-btn";
      readMore.textContent = "Read more";
      readMore.setAttribute("aria-expanded", "false");
      readMore.addEventListener("click", function () {
        expanded = !expanded;
        descText.textContent = expanded ? project.description : truncate(project.description, 120);
        readMore.textContent = expanded ? "Read less" : "Read more";
        readMore.setAttribute("aria-expanded", expanded ? "true" : "false");
      });
      desc.appendChild(readMore);
    }

    var tags = document.createElement("div");
    tags.className = "project-card-tags";
    (project.skills || []).forEach(function (skill) { tags.appendChild(createTag(skill, "skill")); });
    tags.appendChild(createTag(project.level, project.level));
    tags.appendChild(createTag("Time: " + project.time, "time"));

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


  // ----------------------------------------------------------
  // Share My Result ΓÇö build URL and copy to clipboard
  // ----------------------------------------------------------

  var MAX_SHARE_SKILLS = 10;
  var MAX_URL_LENGTH   = 2000;

  // Build a shareable URL from the current form selections.
  // Caps skill count and enforces a max URL length to avoid oversized links.
  function buildShareUrl() {
    var baseUrl = window.location.origin + window.location.pathname;
    var params = new URLSearchParams();
    var allSkills = skillsHidden.value.trim();
    var skillsArr = [];
    var truncatedFlag = false;

    if (allSkills) {
      skillsArr = allSkills.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
      if (skillsArr.length > MAX_SHARE_SKILLS) {
        skillsArr = skillsArr.slice(0, MAX_SHARE_SKILLS);
        truncatedFlag = true;
      }
      params.set("skills", skillsArr.join(", "));
    }

    params.set("level", document.getElementById("level").value);
    params.set("interest", document.getElementById("interest").value);
    params.set("time", document.getElementById("time").value);

    var url = baseUrl + "?" + params.toString();

    // Progressively trim skills if URL still exceeds safe browser limit
    while (url.length > MAX_URL_LENGTH && skillsArr.length > 1) {
      skillsArr.pop();
      truncatedFlag = true;
      params.set("skills", skillsArr.join(", "));
      url = baseUrl + "?" + params.toString();
    }

    return { url: url, truncated: truncatedFlag };
  }

  var shareBtn = document.getElementById("share-result-btn");
  var shareToast = document.getElementById("share-toast");
  var shareToastTimeout = null;
  var _shareWasTruncated = false;

  // Show the "Copied!" state on the share button and display the toast.
  function showShareSuccess() {
    if (!shareBtn) return;
    var originalLabel = shareBtn.querySelector(".share-btn-label");
    var labelText = _shareWasTruncated ? "Copied! (some skills trimmed)" : "Copied!";
    if (originalLabel) originalLabel.textContent = labelText;
    shareBtn.classList.add("copied");

    if (shareToast) shareToast.classList.add("show");

    // Auto-reset after 2.5 seconds
    clearTimeout(shareToastTimeout);
    shareToastTimeout = setTimeout(function () {
      if (originalLabel) originalLabel.textContent = "Share My Result";
      shareBtn.classList.remove("copied");
      if (shareToast) shareToast.classList.remove("show");
    }, 2500);
  }

  // Fallback clipboard copy using a hidden textarea (for older browsers)
  function fallbackShareCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.cssText = "position:fixed;top:-9999px;left:-9999px;opacity:0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try { document.execCommand("copy"); showShareSuccess(); } catch (e) { /* silent fail */ }
    document.body.removeChild(ta);
  }

  if (shareBtn) {
    shareBtn.addEventListener("click", function () {
      var result = buildShareUrl();
      var url = result.url;
      _shareWasTruncated = result.truncated;

      // Use Clipboard API with textarea fallback
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () {
          showShareSuccess();
        }).catch(function () {
          fallbackShareCopy(url);
        });
      } else {
        fallbackShareCopy(url);
      }
    });
  }


  // ----------------------------------------------------------
  // Query param validation for shared URLs
  // ----------------------------------------------------------

  var VALID_LEVELS    = ["Beginner", "Intermediate", "Advanced"];
  var VALID_INTERESTS = ["Web", "Data", "Education", "Automation", "Games"];
  var VALID_TIMES     = ["Low", "Medium", "High"];

  // Strip HTML tags and restrict to safe characters for skill values
  function sanitizeSkillValue(raw) {
    if (!raw || typeof raw !== "string") return "";
    // Remove any HTML/script tags
    var cleaned = raw.replace(/<[^>]*>/g, "");
    // Allow only safe characters: letters, digits, spaces, dots, #, +, _, -, /
    cleaned = cleaned.replace(/[^A-Za-z0-9 .#+_\-\/]/g, "");
    return cleaned.trim();
  }

  // Return the value only if it appears in the allowlist, otherwise ""
  function validateDropdownValue(value, allowlist) {
    if (!value || typeof value !== "string") return "";
    var trimmed = value.trim();
    for (var i = 0; i < allowlist.length; i++) {
      if (allowlist[i] === trimmed) return trimmed;
    }
    return "";
  }


  // ----------------------------------------------------------
  // Auto-fill from shared URL query params (no auto-submit)
  // ----------------------------------------------------------

  // Pre-fill form from URL params but require user to click Generate
  (function initFromQueryParams() {
    var params = new URLSearchParams(window.location.search);
    var qSkills   = params.get("skills");
    var qLevel    = params.get("level");
    var qInterest = params.get("interest");
    var qTime     = params.get("time");

    // Only auto-fill if all four params are present
    if (!qSkills || !qLevel || !qInterest || !qTime) return;

    // Validate dropdown values against their allowlists
    var safeLevel    = validateDropdownValue(qLevel, VALID_LEVELS);
    var safeInterest = validateDropdownValue(qInterest, VALID_INTERESTS);
    var safeTime     = validateDropdownValue(qTime, VALID_TIMES);

    // Abort if any dropdown value is invalid
    if (!safeLevel || !safeInterest || !safeTime) return;

    // Sanitize and add each skill from the comma-separated query param
    qSkills.split(",").forEach(function (s) {
      var safe = sanitizeSkillValue(s);
      if (safe) window.addSkill(safe);
    });

    // Set dropdown values to the validated selections
    document.getElementById("level").value = safeLevel;
    document.getElementById("interest").value = safeInterest;
    document.getElementById("time").value = safeTime;

    // Show the prefill banner instead of auto-submitting
    var banner = document.getElementById("share-prefill-banner");
    var bannerClose = document.getElementById("share-prefill-banner-close");
    if (banner) {
      banner.style.display = "flex";
      if (bannerClose) {
        bannerClose.addEventListener("click", function () {
          banner.style.display = "none";
        });
      }
      // Scroll form into view so user sees the pre-filled state
      var formSection = document.getElementById("find-project");
      if (formSection) formSection.scrollIntoView({ behavior: "smooth" });
    }
  })();


  // ----------------------------------------------------------
  // Skill input event listeners
  // ----------------------------------------------------------

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

  var clearBtn = document.getElementById("clear-filters-btn");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      form.reset();
      selectedSkills = [];
      renderSelectedChips();
      syncSkillsHiddenInput();
      updateQuickPickState();
      clearAllErrors();
      hideSuggestions();
      if (techStackSelect) {
        techStackSelect.value = "all";
      }
      hasSearched = false;
      resultsSection.style.display = "none";
      skillsInput.focus();
    });
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

  // ----------------------------------------------------------
  // Form submission and API call
  // ----------------------------------------------------------

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
        skills: JSON.stringify(selectedSkills),
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
        renderResults(data.projects || [], data.message);
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
};

  // ----------------------------------------------------------
  // GitHub modal
  // ----------------------------------------------------------

  var modal = document.getElementById("github-modal-overlay");
  var openModalBtn = document.getElementById("btn-show-github");
  var closeModalBtn = document.getElementById("btn-close-github");
  var fetchBtn = document.getElementById("btn-fetch-github");
  var githubInput = document.getElementById("github-username");
  var errorMsg = document.getElementById("github-modal-error");

  function closeGithubModal() {
    modal.classList.remove("active");
    githubInput.value = "";
    errorMsg.textContent = "";
  }

  if (modal && openModalBtn && closeModalBtn && fetchBtn && githubInput && errorMsg) {
    openModalBtn.addEventListener("click", function () {
      modal.classList.add("active");
      githubInput.focus();
    });
    closeModalBtn.addEventListener("click", closeGithubModal);
    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeGithubModal();
    });
    fetchBtn.addEventListener("click", function (event) {
      event.preventDefault();
      var username = githubInput.value.trim();
      errorMsg.textContent = "";
      if (!username) {
        errorMsg.textContent = "Please enter a GitHub username.";
        return;
      }
      fetchBtn.disabled = true;
      fetchBtn.textContent = "Syncing...";
      fetch("https://api.github.com/users/" + encodeURIComponent(username) + "/repos?sort=updated&per_page=100")
        .then(function (response) {
          if (!response.ok) throw new Error(response.status === 404 ? "Username not found." : "Unable to fetch GitHub repositories.");
          return response.json();
        })
        .then(function (repos) {
          var languages = [];
          repos.forEach(function (repo) {
            if (repo.language && languages.indexOf(repo.language) === -1) languages.push(repo.language);
          });
          if (!languages.length) {
            errorMsg.textContent = "No public languages found.";
            return;
          }
          languages.forEach(window.addSkill);
          closeGithubModal();
        })
        .catch(function (err) {
          if (err.message && err.message.toLowerCase().indexOf("networkerror") !== -1 || err.name === "TypeError") {
            errorMsg.textContent = "Network error: Connection blocked or offline. Please disable adblockers or check your connection.";
          } else {
            errorMsg.textContent = err.message || "Failed to fetch skills.";
          }
          fetchBtn.disabled = false;
          fetchBtn.textContent = "Fetch Skills";
        });
    });
  }
;


// ============================================================
// DETAIL PAGE
// ============================================================
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
      number.className = "code-line-number";
      number.setAttribute("aria-hidden", "true");
      number.textContent = index + 1;
      var content = document.createElement("span");
      content.className = "code-line-content";
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
      var code = Array.prototype.slice.call(codeContentEl.querySelectorAll(".code-line-content"))
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
  var roadmapStorageKey = "devpath-roadmap-progress-" + PROJECT_ID;

  function updateRoadmapProgress() {
    if (!roadmapCheckboxes.length) return;
    var completed = roadmapCheckboxes.filter(function (checkbox) { return checkbox.checked; }).length;
    var percent = Math.round((completed / roadmapCheckboxes.length) * 100);
    roadmapCheckboxes.forEach(function (checkbox) {
      var step = checkbox.closest(".roadmap-step");
      if (step) step.classList.toggle("completed", checkbox.checked);
    });
    if (progressFill) progressFill.style.width = percent + "%";
    if (progressText) progressText.textContent = percent + "% completed";
    if (progressBar) progressBar.setAttribute("aria-valuenow", String(percent));
    try {
      localStorage.setItem(roadmapStorageKey, JSON.stringify(roadmapCheckboxes.map(function (checkbox) {
        return checkbox.checked;
      })));
    } catch (err) {}
  }

  try {
    var saved = JSON.parse(localStorage.getItem(roadmapStorageKey) || "[]");
    roadmapCheckboxes.forEach(function (checkbox, index) {
      checkbox.checked = !!saved[index];
    });
  } catch (err) {}
  roadmapCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", updateRoadmapProgress);
  });
  updateRoadmapProgress();

  if (completionBtn) {
    completionBtn.addEventListener("click", function () {
      recordCompletion(PROJECT_ID, typeof PROJECT_TITLE !== "undefined" ? PROJECT_TITLE : "");
      showAchievementToast("Project completed", "Nice work finishing this project.");
    });
  }
})();


// ============================================================
// Scroll-to-top / scroll-to-bottom button
// ============================================================
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
})});
