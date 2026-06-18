const PROGRESS_MAX_POINTS = 100;
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
  function renderResults(projects, message) {
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    // Clear out any cards from a previous search before showing new ones
    resultsGrid.innerHTML = "";

    if (!projects || projects.length === 0) { // if no projects returned from api, show "no results" and hide the grid
      resultsGrid.style.display    = "none";
      resultsEmptyEl.style.display = "block";
      if (message && emptyMessageEl) emptyMessageEl.textContent = message;
      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    .empty-completed span {
      font-size: 0.75rem;
    }

    /* Tabs */
    .la-tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      border-bottom: 1px solid var(--border, #e5e7eb);
      padding-bottom: 0.5rem;
    }

    .la-tab {
      background: none;
      border: none;
      padding: 0.5rem 1rem;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      border-radius: 0.5rem;
      color: var(--text-muted, #6b7280);
      transition: all 0.2s;
    }

    .la-tab.active {
      background: #6366f1;
      color: white;
    }
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
      if (emptyMessageEl) { if (message) emptyMessageEl.textContent = message; }
      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    .la-content {
      display: none;
    }

    .la-content.active {
      display: block;
    }

    .leaderboard-list-compact,
    .achievement-list-compact {
      list-style: none;
      margin: 0;
      padding: 0;
      max-height: 200px;
      overflow-y: auto;
    }

    .leaderboard-list-compact li,
    .achievement-list-compact li {
      padding: 0.5rem 0;
      border-bottom: 1px solid var(--border, #e5e7eb);
      font-size: 0.85rem;
    }

    .leaderboard-empty,
    .achievement-empty {
      text-align: center;
      color: var(--text-muted, #6b7280);
      padding: 1.5rem !important;
    }

    .la-footer {
      margin-top: 0.75rem;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border, #e5e7eb);
      font-size: 0.7rem;
      color: var(--text-muted, #6b7280);
      text-align: center;
    recordSearch();
    // Build a card for each project and add it to the grid
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

    /* Responsive */
    @media (max-width: 1024px) {
      .stats-dashboard-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
      }
      
      .profile-bottom-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
      }
      
      .activity-stats-row {
        grid-template-columns: repeat(4, 1fr);
      }
    }

    @media (max-width: 640px) {
      .activity-stats-row {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    /* Dark mode support */
    [data-theme="dark"] .stat-dashboard-card,
    [data-theme="dark"] .completed-card,
    [data-theme="dark"] .leaderboard-achievement-card {
      background: #1f2937;
    }

    [data-theme="dark"] .activity-stat-item {
      background: #374151;
    }

    [data-theme="dark"] .badge-mini {
      background: #374151;
    }
  </style>
</head>

<body>
  <!-- ============================================================
       Navigation
       ============================================================ -->
  <nav class="navbar" id="navbar" aria-label="Main navigation">
    <div class="nav-inner">
      <a href="/" class="nav-logo">Dev<span class="nav-logo-accent">Path</span></a>

      <form id="topic-search-form" class="navbar-search" role="search">
        <input
          type="search"
          id="topic-search"
          autocomplete="off"
          aria-label="Search projects"
          placeholder="Search projects…"
        />
        <button class="navbar-search-btn" type="submit" aria-label="Search">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M21 21l-4.35-4.35m1.85-5.15a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </form>

      <div class="nav-right">
        <div class="nav-links">
          <a href="#home" class="nav-link">Home</a>
          <a href="#how-it-works" class="nav-link">How It Works</a>
          <a href="#features" class="nav-link">Features</a>
          <a href="#find-project" class="nav-link">Find Project</a>
          <a href="/compare" class="nav-link">Compare</a>
          <a href="/contact" class="nav-link">Contact</a>
        </div>

        <div class="nav-actions">
          <a href="https://github.com/komalharshita/DevPath" target="_blank" rel="noopener noreferrer"
            class="nav-btn-outline">GitHub</a>
          <button class="theme-toggle" id="theme-toggle-desktop" aria-pressed="false"
            aria-label="Switch to dark mode">
            <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
            <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          </button>
        </div>
      </div>

      <button class="nav-mobile-toggle" id="nav-mobile-toggle" aria-label="Toggle navigation"
        aria-expanded="false" aria-controls="nav-mobile-menu">
        <span></span><span></span><span></span>
      </button>
    </div>

    <div class="nav-mobile-menu" id="nav-mobile-menu" role="menu">
      <form id="topic-search-form-mobile" class="navbar-search navbar-search--mobile" role="search">
        <input type="search" id="topic-search-mobile" autocomplete="off" aria-label="Search projects"
          placeholder="Search projects…" />
        <button class="navbar-search-btn" type="submit" aria-label="Search">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M21 21l-4.35-4.35m1.85-5.15a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </form>
      <a href="#home" class="nav-mobile-link" role="menuitem">Home</a>
      <a href="#how-it-works" class="nav-mobile-link" role="menuitem">How It Works</a>
      <a href="#features" class="nav-mobile-link" role="menuitem">Features</a>
      <a href="#find-project" class="nav-mobile-link" role="menuitem">Find Project</a>
      <a href="/compare" class="nav-mobile-link" role="menuitem">Compare</a>
      <a href="/contact" class="nav-mobile-link" role="menuitem">Contact</a>
      <a href="https://github.com/komalharshita/DevPath" target="_blank" rel="noopener noreferrer"
        class="nav-mobile-link" role="menuitem">GitHub</a>
      <button class="nav-mobile-link theme-toggle" id="theme-toggle-mobile"
        aria-pressed="false" aria-label="Switch to dark mode" role="menuitem">
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
        <span class="theme-toggle-label">Dark Mode</span>
      </button>
    </div>
  </nav>

  <!-- ============================================================
       No-Script Fallback
       ============================================================ -->
  <noscript>
    <div class="noscript-warning">
      <p>JavaScript is required to use DevPath. Please enable JavaScript in your browser settings and reload the page.
      </p>
    </div>
  </noscript>

  <!-- ============================================================
       Hero Section
       ============================================================ -->
  <section class="hero" id="home">
    <div class="hero-inner">
      <div class="hero-copy">
        <div class="hero-badge">
          <span class="hero-badge-dot"></span>
          Open Source Developer Tool
        </div>

        <h1 class="hero-heading">
          Build Projects<br>
          <span class="hero-heading-accent">That Actually Matter</span>
        </h1>

        <p class="hero-subtext">
          Tell DevPath what you know, what interests you, and how much time
          you have. Get matched to real coding projects with step-by-step
          roadmaps and ready-to-run starter code.
        </p>

        <div class="hero-cta-row">
          <a href="#find-project" class="btn-hero-primary">Start Finding Projects</a>
          <a href="#how-it-works" class="btn-hero-ghost">See How It Works</a>
        </div>
      </div>

      <div class="hero-visual">
        <div class="hero-visual-card hero-visual-card--top">
          <div class="hvc-icon hvc-icon--blue">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round">
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
          </div>
          <div class="hvc-text">
            <span class="hvc-title">Starter Code Ready</span>
            <span class="hvc-sub">Download and start immediately</span>
          </div>
        </div>

        <div class="hero-visual-main">
          <div class="hvm-header">
            <span class="hvm-dot hvm-dot--red"></span>
            <span class="hvm-dot hvm-dot--yellow"></span>
            <span class="hvm-dot hvm-dot--green"></span>
            <span class="hvm-filename">expense_tracker.py</span>
          </div>
          <div class="hvm-code">
            <span class="hvm-line"><span class="hvm-kw">def</span> <span class="hvm-fn">add_expense</span>(category, amount):</span>
            <span class="hvm-line hvm-indent"><span class="hvm-cm"># Save entry to CSV</span></span>
            <span class="hvm-line hvm-indent">date <span class="hvm-op">=</span> datetime.now()</span>
            <span class="hvm-line hvm-indent"><span class="hvm-kw">with</span> open(DATA_FILE) <span class="hvm-kw">as</span> f:</span>
            <span class="hvm-line hvm-indent2">writer.writerow([date, ...])</span>
            <span class="hvm-line">&nbsp;</span>
            <span class="hvm-line"><span class="hvm-kw">def</span> <span class="hvm-fn">monthly_summary</span>():</span>
            <span class="hvm-line hvm-indent"><span class="hvm-cm"># TODO: implement</span></span>
            <span class="hvm-line hvm-indent"><span class="hvm-kw">pass</span></span>
          </div>
        </div>

        <div class="hero-visual-card hero-visual-card--bottom">
          <div class="hvc-icon hvc-icon--green">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          <div class="hvc-text">
            <span class="hvc-title">7-Step Roadmap</span>
            <span class="hvc-sub">Clear path from start to finish</span>
          </div>
        </div>
      </div>
    </div>

    <div class="hero-bg-grid"></div>
    <div class="hero-blob hero-blob-1"></div>
    <div class="hero-blob hero-blob-2"></div>
  </section>

  <!-- ============================================================
       Statistics Cards (Dynamic)
       ============================================================ -->
  <section class="stats-section">
    <div class="container">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon stat-icon--indigo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_projects }}</span>
            <span class="stat-label">Real Projects</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon--yellow">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path
                d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.unique_skills }}</span>
            <span class="stat-label">Unique Skills</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.beginner_friendly }}</span>
            <span class="stat-label">Beginner Friendly</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       Progress + Achievements (REDESIGNED)
       ============================================================ -->
  <section class="progress-section" id="progress">
    <div class="container">
      <div class="section-eyebrow">Your DevPath Profile</div>
      <h2 class="section-title">Track Progress, Unlock Badges, and See Your Growth</h2>
      <p class="section-sub">Local progress is saved in your browser so you can build momentum without signing in.</p>

      <div class="stats-dashboard-grid">
        <div class="stat-dashboard-card points-card">
          <div class="stat-dashboard-header">
            <span class="stat-dashboard-title">Total Points</span>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </div>
          <div class="stat-dashboard-value" id="progress-points">0</div>
          <div class="stat-dashboard-progress">
            <div class="progress-meter">
              <span class="progress-meter-fill" id="progress-meter-fill" style="width: 0%;">0%</span>
            </div>
          </div>
          <div class="stat-dashboard-footer">
            <span>Next badge at 100 pts</span>
            <button type="button" id="reset-progress-btn" class="reset-btn-mini">Reset</button>
          </div>
        </div>

        <div class="stat-dashboard-card badges-card">
          <div class="stat-dashboard-header">
            <span class="stat-dashboard-title">Badges Earned</span>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L15 8.5L22 9.5L17 14L18.5 21L12 17.5L5.5 21L7 14L2 9.5L9 8.5L12 2z"/>
            </svg>
          </div>
          <div class="badges-grid-mini" id="progress-badges"></div>
          <div class="stat-dashboard-footer">
            <span>Unlock achievements as you explore</span>
          </div>
        </div>

        <div class="stat-dashboard-card activity-card">
          <div class="stat-dashboard-header">
            <span class="stat-dashboard-title">Your Activity</span>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="activity-stats-row">
            <div class="activity-stat-item">
              <span class="activity-stat-value" id="searches-count">0</span>
              <span class="activity-stat-label">Searches</span>
            </div>
            <div class="activity-stat-item">
              <span class="activity-stat-value" id="projects-viewed-count">0</span>
              <span class="activity-stat-label">Viewed</span>
            </div>
            <div class="activity-stat-item">
              <span class="activity-stat-value" id="code-opens-count">0</span>
              <span class="activity-stat-label">Code Opens</span>
            </div>
            <div class="activity-stat-item">
              <span class="activity-stat-value" id="projects-completed-count">0</span>
              <span class="activity-stat-label">Completed</span>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-bottom-grid">
        <div class="completed-card">
          <div class="completed-header">
            <h3>Completed Projects</h3>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="completed-list" id="completed-history-list">
            <div class="empty-completed">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              <p>No completed projects yet</p>
              <span>Start a project to see it here</span>
            </div>
          </div>
        </div>

        <div class="leaderboard-achievement-card">
          <div class="la-tabs">
            <button class="la-tab active" data-tab="leaderboard">🏆 Leaderboard</button>
            <button class="la-tab" data-tab="achievements">✨ Achievements</button>
          </div>
          
          <div class="la-content active" id="leaderboard-content">
            <ol class="leaderboard-list-compact" id="leaderboard-list">
              <li class="leaderboard-empty">Complete projects to see rankings</li>
            </ol>
            <div class="la-footer">
              <span>Local rankings • Updated in real-time</span>
            </div>
          </div>
          
          <div class="la-content" id="achievements-content">
            <ul class="achievement-list-compact" id="achievement-list">
              <li class="achievement-empty">Complete actions to earn achievements</li>
            </ul>
            <div class="la-footer">
              <span>Keep coding to unlock more!</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <div class="achievement-toast" id="achievement-toast" role="status" aria-live="polite"></div>

  <!-- ============================================================
       Language / Skill Strip
       ============================================================ -->
  <div class="skill-strip">
    <div class="skill-strip-inner">
      <span class="skill-strip-label">Supports skills including:</span>
      <div class="skill-strip-items">
        <span class="ss-item-indigo">Python</span>
        <span class="ss-item-green">JavaScript</span>
        <span class="ss-item-purple">HTML / CSS</span>
        <span class="ss-item-pink">Flask</span>
        <span class="ss-item-green">SQL</span>
        <span class="ss-item-purple">React</span>
        <span class="ss-item-pink">Node.js</span>
        <span class="ss-item-green">pandas</span>
        <span class="ss-item-pink">C++</span>
        <span class="ss-item-indigo">Java</span>
        <span class="ss-item-green">TypeScript</span>
        <span class="ss-item-purple">Go</span>
        <span class="ss-item-pink">Rust</span>
        <span class="ss-item-green">C#</span>
        <span class="ss-item-purple">Kotlin</span>
      </div>
    </div>
  </div>

  <!-- ============================================================
       How It Works
       ============================================================ -->
  <section class="how-section" id="how-it-works">
    <div class="container">
      <div class="section-eyebrow">How DevPath Works</div>
      <h2 class="section-title">From Your Skills to Your<br>Next Project in Minutes</h2>
      <p class="section-sub">Three simple steps. No account required. No fluff.</p>

      <div class="steps-grid">
        <div class="step-card">
          <div class="step-num">01</div>
          <h3>Enter Your Skills</h3>
          <p>Type your programming skills or click quick-select chips. Add as many as you like.</p>
        </div>
        <div class="step-connector">
          <svg width="32" height="16" viewBox="0 0 32 16">
            <path d="M0 8 H28 M22 2 L30 8 L22 14" stroke="currentColor" stroke-width="2" fill="none"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <div class="step-card">
          <div class="step-num">02</div>
          <h3>Set Your Preferences</h3>
          <p>Select your experience level, area of interest, and how much time you can commit.</p>
        </div>
        <div class="step-connector">
          <svg width="32" height="16" viewBox="0 0 32 16">
            <path d="M0 8 H28 M22 2 L30 8 L22 14" stroke="currentColor" stroke-width="2" fill="none"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <div class="step-card">
          <div class="step-num">03</div>
          <h3>Get Matched Projects</h3>
          <p>DevPath returns your top three matched projects with roadmaps and starter code.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       Features Section
       ============================================================ -->
  <section class="features-section" id="features">
    <div class="container">
      <div class="section-eyebrow">What You Get</div>
      <h2 class="section-title">Everything You Need to Start Building</h2>
      <p class="section-sub">Every recommendation comes with practical resources — not just a project name.</p>

      <div class="features-grid">
        <div class="feature-card feature-card--pink">
          <div class="feature-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <h3>Personalized Matches</h3>
          <p>Projects are scored against your exact skills, level, and interest — not pulled from a generic list.</p>
          <a href="#find-project" class="feature-card-link">Try it now</a>
        </div>

        <div class="feature-card feature-card--yellow">
          <div class="feature-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          <h3>Step-by-Step Roadmaps</h3>
          <p>Each project includes a numbered roadmap so you always know what to build next, without guessing.</p>
          <a href="#find-project" class="feature-card-link">Explore roadmaps</a>
        </div>

        <div class="feature-card feature-card--purple">
          <div class="feature-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
          </div>
          <h3>Starter Code Included</h3>
          <p>Download a working template for every project. Skip the blank-page problem and start building immediately.</p>
          <a href="#find-project" class="feature-card-link">Get starter code</a>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       Find Project Form Section
       ============================================================ -->
  <section class="form-section" id="find-project">
    <div class="container">
      <div class="section-eyebrow">Get Your Recommendations</div>
      <h2 class="section-title">Find Your Next Project</h2>
      <p class="section-sub">Fill in your details below and DevPath will match you to the most relevant projects.</p>

      <div class="form-card-outer">
        <div class="form-card" id="form-section">
          <form id="recommend-form" novalidate>
            <div class="form-group">
              <div class="form-label-row" style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 8px;">
                <label for="skills-input">
                  Your Skills
                  <button type="button" class="tooltip" aria-label="Skills help" aria-describedby="skills-tooltip">
                    <span aria-hidden="true">ⓘ</span>
                    <span id="skills-tooltip" class="tooltip-text" role="tooltip">
                      Add technologies, programming languages, or tools you know like Python, React, Git, SQL, etc.
                    </span>
                  </button>
                </label>

                <div class="github-inline-trigger" id="github-trigger-wrap" style="line-height: 1.2;">
                  <button type="button" id="btn-show-github" class="resource-link"
                    style="padding: 4px 8px; border-radius: var(--r-xs); font-size: 0.75rem; gap: 6px;">
                    <svg style="width:14px; fill:currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.041-1.416-4.041-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                    </svg>
                    <span>Import from GitHub</span>
                  </button>
                </div>
              </div>
              <div class="skill-input-wrap" id="skill-input-wrap">
                <div class="skill-chips-selected" id="skill-chips-selected"></div>
                <input type="text" id="skills-input" placeholder="Type a skill and press Enter..."
                  autocomplete="off" aria-haspopup="listbox" aria-expanded="false" aria-controls="skills-suggestions" />
                <div id="skills-suggestions" class="skills-suggestions"></div>
              </div>
              <input type="hidden" id="skills" name="skills" />
              <span class="form-hint">
                Add one or more skills you are comfortable with. Example: Python, React, SQL, Git.
              </span>
              <div class="form-error-msg" id="skills-error"></div>
            </div>

            <div class="skill-chips-row" id="skill-chips-available">
              <button type="button" class="skill-chip" data-skill="Python">Python</button>
              <button type="button" class="skill-chip" data-skill="JavaScript">JavaScript</button>
              <button type="button" class="skill-chip" data-skill="HTML">HTML</button>
              <button type="button" class="skill-chip" data-skill="CSS">CSS</button>
              <button type="button" class="skill-chip" data-skill="Flask">Flask</button>
              <button type="button" class="skill-chip" data-skill="SQL">SQL</button>
              <button type="button" class="skill-chip" data-skill="React">React</button>
              <button type="button" class="skill-chip" data-skill="Node.js">Node.js</button>
              <button type="button" class="skill-chip" data-skill="C++">C++</button>
              <button type="button" class="skill-chip" data-skill="Java">Java</button>
              <button type="button" class="skill-chip" data-skill="TypeScript">TypeScript</button>
              <button type="button" class="skill-chip" data-skill="Go">Go</button>
              <button type="button" class="skill-chip" data-skill="Rust">Rust</button>
              <button type="button" class="skill-chip" data-skill="C#">C#</button>
              <button type="button" class="skill-chip" data-skill="Kotlin">Kotlin</button>
              <button type="button" class="skill-chip" data-skill="Django">Django</button>
              <button type="button" class="skill-chip" data-skill="FastAPI">FastAPI</button>
              <button type="button" class="skill-chip" data-skill="Express.js">Express.js</button>
              <button type="button" class="skill-chip" data-skill="Next.js">Next.js</button>
              <button type="button" class="skill-chip" data-skill="Vue.js">Vue.js</button>
              <button type="button" class="skill-chip" data-skill="Angular">Angular</button>
              <button type="button" class="skill-chip" data-skill="Tailwind CSS">Tailwind CSS</button>
              <button type="button" class="skill-chip" data-skill="Bootstrap">Bootstrap</button>
              <button type="button" class="skill-chip" data-skill="PostgreSQL">PostgreSQL</button>
              <button type="button" class="skill-chip" data-skill="MySQL">MySQL</button>
              <button type="button" class="skill-chip" data-skill="MongoDB">MongoDB</button>
              <button type="button" class="skill-chip" data-skill="Redis">Redis</button>
              <button type="button" class="skill-chip" data-skill="Docker">Docker</button>
              <button type="button" class="skill-chip" data-skill="Kubernetes">Kubernetes</button>
              <button type="button" class="skill-chip" data-skill="Git">Git</button>
              <button type="button" class="skill-chip" data-skill="Linux">Linux</button>
              <button type="button" class="skill-chip" data-skill="Pandas">Pandas</button>
              <button type="button" class="skill-chip" data-skill="NumPy">NumPy</button>
              <button type="button" class="skill-chip" data-skill="TensorFlow">TensorFlow</button>
              <button type="button" class="skill-chip" data-skill="PyTorch">PyTorch</button>
              <button type="button" class="skill-chip" data-skill="AWS">AWS</button>
              <button type="button" class="skill-chip" data-skill="GraphQL">GraphQL</button>
              <button type="button" class="skill-chip" data-skill="Jest">Jest</button>
              <button type="button" class="skill-chip" data-skill="pytest">pytest</button>
              <button type="button" class="skill-chip" data-skill="Webpack">Webpack</button>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="level">Experience Level</label>
                <div class="select-wrap">
                  <select id="level" name="level">
                    <option value="" disabled selected>Select level</option>
                    {% for level in available_levels %}
                    <option value="{{ level }}">{{ level }}</option>
                    {% endfor %}
                  </select>
                </div>
                <span class="form-hint">Select your current proficiency level such as Beginner or Intermediate.</span>
                <div class="form-error-msg" id="level-error"></div>
              </div>

              <div class="form-group">
                <label for="interest">
                  Area of Interest
                  <button type="button" class="tooltip" aria-label="Interest help" aria-describedby="interest-tooltip">
                    ⓘ
                    <span id="interest-tooltip" class="tooltip-text" role="tooltip">
                      Choose the type of projects you enjoy building or want to learn more about.
                    </span>
                  </button>
                </label>
                <div class="select-wrap">
                  <select id="interest" name="interest">
                    <option value="" disabled selected>Select interest</option>
                    <option value="Web">Web Development</option>
                    <option value="Data">Data and Analytics</option>
                    <option value="Education">Education Tools</option>
                    <option value="Automation">Automation</option>
                    <option value="Games">Games</option>
                    <option value="Cybersecurity">CyberSecurity/Ethical Hacking</option>
                    <option value="Devops">DevOps / Cloud Computing</option>
                    <option value="Backend">Backend APIs</option>
                    <option value="Tools">Developer Tools</option>
                    <option value="Productivity">Productivity</option>
                    <option value="Business Logic">Business Logic</option>
                    <option value="Mobile">Mobile Development</option>
                    <option value="Machine Learning/AI">Machine Learning/AI</option>
                  </select>
                </div>
                <span class="form-hint">Pick the domain you want to explore such as Web Development, Automation, or Games.</span>
                <div class="form-error-msg" id="interest-error"></div>
              </div>
            </div>

            <div class="form-group">
              <label for="time">
                Time Availability
                <span class="tooltip" title="Estimate how much time you can realistically dedicate to building the project.">
                  ⓘ
                </span>
              </label>
              <div class="select-wrap">
                <select id="time" name="time">
                  <option value="" disabled selected>How much time can you commit?</option>
                  <option value="Low">Low — a few hours total</option>
                  <option value="Medium">Medium — across a weekend</option>
                  <option value="High">High — a week or more</option>
                </select>
              </div>
              <span class="form-hint">Include coding, debugging, learning, and reviewing time in your estimate.</span>
              <div class="form-error-msg" id="time-error"></div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-submit" id="submit-btn">
                <span id="btn-label">Generate My Projects</span>
                <span id="btn-loading" style="display:none;">Finding matches...</span>
              </button>
              <button type="button" class="btn-clear" id="clear-filters-btn">
                <span>Clear Filters</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       Results Section
       ============================================================ -->
  <section class="results-section" id="results-section" style="display:none;" aria-live="polite" aria-atomic="false">
    <div class="container">
      <div class="section-eyebrow">Your Matches</div>
      <h2 class="section-title">Recommended Projects</h2>
      <p class="section-sub" id="results-subtitle">Based on your inputs, here are your top matches.</p>

      <div id="results-loading" aria-live="polite" aria-atomic="true" style="display:none;">
        <div class="loading-box">
          <div class="loading-dots"><span></span><span></span><span></span></div>
          <p>Finding the best projects for you...</p>
        </div>
      </div>

      <div id="results-empty" style="display:none;">
        <div class="empty-state">
          <div class="empty-icon">
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
              stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </div>
          <h3>No Projects Found</h3>
          <p id="empty-message">Try adjusting your skills or selecting a different interest area.</p>
          <button class="btn-try-again" onclick="document.getElementById('find-project').scrollIntoView({behavior:'smooth'})">Try Different Inputs</button>
        </div>
      </div>

      <div class="results-grid" id="results-grid"></div>

      <div class="saved-projects-panel" id="saved-projects-panel">
        <div class="saved-projects-header">
          <div>
            <h3>Saved Projects</h3>
            <p>Shortlist ideas you want to revisit later.</p>
          </div>
          <span class="saved-projects-count" id="saved-projects-count">0 saved</span>
        </div>
        <div class="saved-projects-list" id="saved-projects-list"></div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       CTA Banner
       ============================================================ -->
  <section class="cta-section">
    <div class="container">
      <div class="cta-inner">
        <h2>Start Building.<br><span class="cta-accent">A New Skill</span> Awaits.</h2>
        <p>Find a project that challenges you and grow with every line of code.</p>
        <a href="#find-project" class="btn-cta">Find My Project</a>
      </div>
    </div>
  </section>

  <!-- ============================================================
       Our Story / About Us
       ============================================================ -->
  <section class="features-section" id="our-story">
    <div class="container">
      <div class="section-eyebrow">About Us</div>
      <h2 class="section-title">Our Story</h2>
      <p class="section-sub">DevPath was built to help learners move from scattered tutorials to projects with a clear
        path, practical code, and meaningful momentum.</p>

      <div class="features-grid">
        <div class="feature-card">
          <h3>Why it exists</h3>
          <p>Too many project ideas stop at the title. DevPath focuses on the next steps that make starting and
            finishing feel manageable.</p>
        </div>
        <div class="feature-card">
          <h3>How it helps</h3>
          <p>Each recommendation includes a roadmap and starter code so users can spend time building instead of
            searching for structure.</p>
        </div>
        <div class="feature-card">
          <h3>What it leads to</h3>
          <p>A smoother path from curiosity to a finished project, with fewer dead ends and more confidence along the
            way.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       Footer
       ============================================================ -->
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-col footer-col--brand">
        <span class="footer-logo">Dev<span class="footer-logo-accent">Path</span></span>
        <p class="footer-tagline">Open source. Built for learners, by learners.</p>
        <p class="footer-tagline">Helping developers find meaningful projects to build their skills.</p>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Quick Links</h4>
        <ul class="footer-links-list">
          <li><a href="#home">Home</a></li>
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#find-project">Find Project</a></li>
          <li><a href="/contact">Contact Us</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">Resources</h4>
        <ul class="footer-links-list">
          <li><a href="/project/1">Sample Project</a></li>
          <li><a href="https://github.com/komalharshita/DevPath" target="_blank" rel="noopener noreferrer">GitHub</a></li>
          <li><a href="https://github.com/komalharshita/DevPath/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener noreferrer">Contributing Guide</a></li>
          <li><a href="https://github.com/komalharshita/DevPath/issues" target="_blank" rel="noopener noreferrer">Report an Issue</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-col-title">About Us</h4>
        <ul class="footer-links-list">
          <li><a href="#our-story">Our Story</a></li>
          <li><a href="https://github.com/komalharshita/DevPath" target="_blank" rel="noopener noreferrer">Open Source</a></li>
          <li><a href="https://github.com/komalharshita/DevPath/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">License</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>DevPath is open source. Licensed under the MIT License.</p>
      <div class="footer-bottom-links">
        <a href="#our-story">About Us</a>
        <a href="https://github.com/komalharshita/DevPath/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">Project License</a>
      </div>
    </div>
  </footer>

  <!-- GitHub Modal Overlay -->
  <div class="code-panel-overlay" id="github-modal-overlay" style="align-items: center; justify-content: center; opacity: 1;">
    <div class="sidebar-card" style="width: 100%; max-width: 400px; margin: 20px; z-index: 400; box-shadow: 0 20px 50px rgba(0,0,0,0.3);">
      <div class="sidebar-card-title">
        <svg style="width:18px; fill:var(--indigo-600)" viewBox="0 0 24 24">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.041-1.416-4.041-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
        </svg>
        Sync with GitHub
      </div>

      <p class="sidebar-card-desc" style="margin-bottom: 20px;">Enter your username to import coding languages from your
        top repositories into the skills list.<br /> Note: We use stars to determine top repositories</p>

      <div class="form-group" style="margin-bottom: 20px;">
        <div class="skill-input-wrap">
          <span style="color:var(--gray-400); font-family:var(--font-mono); font-size:0.8rem; margin-left:8px;">@</span>
          <input type="text" id="github-username" placeholder="username" style="border:none; outline:none; flex:1; padding:10px;">
        </div>
        <div class="form-error-msg" id="github-modal-error"></div>
      </div>

      <div style="display: flex; gap: 12px;">
        <button type="button" id="btn-fetch-github" class="btn-primary" style="flex: 2; padding: 10px; font-size: 0.85rem;">Fetch Skills</button>
        <button type="button" id="btn-close-github" class="btn-view-code-sm" style="flex: 1; border-color: var(--border); color: var(--text-body);">Cancel</button>
      </div>
    </div>
  </div>

  <style>
    .form-actions {
      display: flex;
      gap: 12px;
      margin-top: 20px;
      align-items: center;
    }

    .btn-clear {
      background-color: #f3f4f6;
      color: #1f2937;
      border: 1px solid #d1d5db;
      padding: 12px 24px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .btn-clear:hover {
      background-color: #e5e7eb;
    }
  </style>

  <script src="/static/data/skills.js"></script>

  <button id="scroll-top-btn" aria-label="Scroll to top" title="Scroll to top">
    <svg id="scroll-btn-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="18 15 12 9 6 15"/>
    </svg>
  </button>

  <script src="/static/script.js"></script>
  
  <script>
    // Tab switching for leaderboard/achievements (adds to your existing JS)
    document.addEventListener('DOMContentLoaded', function() {
      const tabs = document.querySelectorAll('.la-tab');
      tabs.forEach(tab => {
        tab.addEventListener('click', function() {
          const parent = this.closest('.leaderboard-achievement-card');
          if (parent) {
            parent.querySelectorAll('.la-tab').forEach(t => t.classList.remove('active'));
            parent.querySelectorAll('.la-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            if (tabId === 'leaderboard') {
              const leaderboardContent = parent.querySelector('#leaderboard-content');
              if (leaderboardContent) leaderboardContent.classList.add('active');
            } else {
              const achievementsContent = parent.querySelector('#achievements-content');
              if (achievementsContent) achievementsContent.classList.add('active');
            }
          }
        });
      });
    });
  </script>
</body>

</html>
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
        time: document.getElementById("time").value
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
        renderResults(data.projects || [], data.message);
      })
      .catch(function (err) {
        setLoadingState(false);
        var general = document.getElementById("form-error-general");
        if (general) general.textContent = err.message || "An unexpected error occurred. Please try again.";
      });
  })};

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
