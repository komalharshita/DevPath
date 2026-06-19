// script.js — DevPath client-side logic
//
// Responsibilities:
//   - Theme toggle & preview modal
//   - Mobile navigation toggle
//   - Skill chip manager (add/remove skills)
//   - Form validation with per-field error messages
//   - Recommendation API call and loading states
//   - Result card rendering
//   - Code viewer panel (detail page)
//   - Progress tracking & achievements
//   - Share URL builder
//   - Scroll-to-top button

// ============================================================
// POINTS CONSTANTS
// ============================================================
var POINTS_PER_SEARCH = 10;
var POINTS_PER_VIEW = 5;
var POINTS_PER_CODE_OPEN = 3;
var POINTS_PER_COMPLETION = 20;
var PROGRESS_MAX_POINTS = 200;

// ============================================================
// THEME — runs immediately so there is no flash of wrong theme
// ============================================================
(function () {
  var html = document.documentElement;

  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("theme", theme);
    } catch (e) {}
    var isDark = theme === "dark";
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      btn.setAttribute(
        "aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode",
      );
    });
  }

  var saved;
  try {
    saved = localStorage.getItem("theme");
  } catch (e) {}
  applyTheme(saved || html.getAttribute("data-theme") || "light");

  requestAnimationFrame(function () {
    html.classList.add("theme-ready");
  });

  document.addEventListener("click", function (e) {
    var toggle = e.target.closest(".theme-toggle");
    if (!toggle) return;
    e.preventDefault();
    var current = html.getAttribute("data-theme") || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  });
})();

// ============================================================
// THEME PREVIEW MODAL
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
  var modalHtml =
    '<div id="theme-preview-modal" class="theme-modal-overlay" aria-hidden="true" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:10000;backdrop-filter:blur(4px);align-items:center;justify-content:center;">' +
    '<div class="theme-modal-content" role="dialog" aria-modal="true" aria-labelledby="theme-modal-title" style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:1.5rem;max-width:500px;width:90%;box-shadow:var(--shadow-xl);">' +
    '<div class="theme-modal-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">' +
    '<h2 id="theme-modal-title" style="font-size:1.25rem;margin:0;color:var(--text-heading);">Choose a Theme</h2>' +
    '<button id="close-theme-modal" class="btn-clear" aria-label="Close modal" style="background:transparent;border:none;font-size:1.5rem;cursor:pointer;color:var(--text-light);">&times;</button>' +
    "</div>" +
    '<div class="theme-preview-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">' +
    '<button class="theme-preview-card" data-theme-target="light" style="background:transparent;border:2px solid var(--border);border-radius:var(--r-md);padding:1rem;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:1rem;transition:all 0.2s ease;">' +
    '<div style="width:100%;background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;padding:8px;display:flex;flex-direction:column;gap:6px;">' +
    '<div style="width:100%;height:12px;background:#f1f5f9;border-radius:3px;"></div>' +
    '<div style="width:100%;height:6px;background:#cbd5e1;border-radius:2px;"></div>' +
    '<div style="width:60%;height:6px;background:#cbd5e1;border-radius:2px;"></div>' +
    '<div style="width:100%;margin-top:4px;padding:4px 0;background:#3b82f6;border-radius:3px;color:#fff;font-size:8px;text-align:center;font-weight:bold;">Button</div>' +
    '</div><span style="font-weight:600;color:var(--text-heading);">Light Theme</span></button>' +
    '<button class="theme-preview-card" data-theme-target="dark" style="background:transparent;border:2px solid var(--border);border-radius:var(--r-md);padding:1rem;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:1rem;transition:all 0.2s ease;">' +
    '<div style="width:100%;background:#0f172a;border:1px solid #1e293b;border-radius:6px;padding:8px;display:flex;flex-direction:column;gap:6px;">' +
    '<div style="width:100%;height:12px;background:#1e293b;border-radius:3px;"></div>' +
    '<div style="width:100%;height:6px;background:#334155;border-radius:2px;"></div>' +
    '<div style="width:60%;height:6px;background:#334155;border-radius:2px;"></div>' +
    '<div style="width:100%;margin-top:4px;padding:4px 0;background:#60a5fa;border-radius:3px;color:#0f172a;font-size:8px;text-align:center;font-weight:bold;">Button</div>' +
    '</div><span style="font-weight:600;color:var(--text-heading);">Dark Theme</span></button>' +
    "</div></div></div>";

  document.body.insertAdjacentHTML("beforeend", modalHtml);

  var modal = document.getElementById("theme-preview-modal");
  var closeBtn = document.getElementById("close-theme-modal");
  var cards = document.querySelectorAll(".theme-preview-card");
  var html = document.documentElement;

  function syncThemeCards(theme) {
    cards.forEach(function (card) {
      card.style.borderColor =
        card.getAttribute("data-theme-target") === theme
          ? "var(--accent)"
          : "var(--border)";
    });
  }

  syncThemeCards(html.getAttribute("data-theme") || "light");

  document.querySelectorAll(".theme-toggle").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    });

  function closeModal() {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
  }

  closeBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", function (e) {
    if (e.target === modal) closeModal();
  });

  cards.forEach(function (card) {
    card.addEventListener("click", function () {
      var theme = this.getAttribute("data-theme-target");
      html.setAttribute("data-theme", theme);
      try {
        localStorage.setItem("theme", theme);
      } catch (e) {}
      syncThemeCards(theme);
      setTimeout(closeModal, 150);
    });
    card.addEventListener("mouseenter", function () {
      if (
        this.getAttribute("data-theme-target") !==
        html.getAttribute("data-theme")
      )
        this.style.borderColor = "var(--gray-400)";
    });
    card.addEventListener("mouseleave", function () {
      if (
        this.getAttribute("data-theme-target") !==
        html.getAttribute("data-theme")
      )
        this.style.borderColor = "var(--border)";
    });
  });
});

// ============================================================
// MOBILE NAV
// ============================================================
(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu = document.getElementById("nav-mobile-menu");
  if (!toggle || !menu) return;

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
})();

// ============================================================
// PROGRESS TRACKING
// ============================================================
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
    roadmap_runner: false,
  },
  bestScore: 0,
};

function loadProgressState() {
  try {
    var saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (!saved || typeof saved !== "object") return;
    progress = Object.assign(progress, saved);
    progress.viewedProjects = Array.isArray(saved.viewedProjects)
      ? saved.viewedProjects
      : [];
    progress.completedProjects = Array.isArray(saved.completedProjects)
      ? saved.completedProjects
      : [];
    progress.achievements = Array.isArray(saved.achievements)
      ? saved.achievements
      : [];
    progress.badges = Object.assign(progress.badges, saved.badges || {});
  } catch (e) {
    console.warn("Unable to load progress state", e);
  }
}

function saveProgressState() {
  try {
    progress.bestScore = Math.max(
      progress.bestScore || 0,
      progress.points || 0,
    );
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch (e) {
    console.warn("Unable to save progress state", e);
  }
}

function computeProgressPoints() {
  progress.points =
    progress.searches * POINTS_PER_SEARCH +
    progress.projectViews * POINTS_PER_VIEW +
    progress.codeOpens * POINTS_PER_CODE_OPEN +
    progress.completions * POINTS_PER_COMPLETION;
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
  window.clearTimeout(showAchievementToast._t);
  showAchievementToast._t = window.setTimeout(function () {
    toast.classList.remove("show");
  }, 3200);
}

function addAchievement(title, detail) {
  if (
    progress.achievements.some(function (a) {
      return a.title === title;
    })
  )
    return;
  progress.achievements.unshift({
    title: title,
    description: detail,
    date: new Date().toLocaleDateString(),
  });
  progress.achievements = progress.achievements.slice(0, 5);
}

function unlockBadge(id, title, detail) {
  if (progress.badges[id]) return;
  progress.badges[id] = true;
  addAchievement(title, detail);
  showAchievementToast("Badge unlocked", title + " — " + detail);
}

function tryUnlockBadges() {
  if (progress.searches >= 1)
    unlockBadge(
      "first_search",
      "First Search",
      "You used DevPath to find your first project.",
    );
  if (progress.projectViews >= 1)
    unlockBadge(
      "project_explorer",
      "Project Explorer",
      "You viewed a project detail.",
    );
  if (progress.codeOpens >= 1)
    unlockBadge("code_starter", "Code Starter", "You opened starter code.");
  if (progress.completions >= 1)
    unlockBadge(
      "completionist",
      "Completionist",
      "You marked a project complete.",
    );
  if (progress.searches >= 5)
    unlockBadge("roadmap_runner", "Roadmap Runner", "You searched five times.");
}

function projectIsCompleted(projectId) {
  return progress.completedProjects.some(function (item) {
    return (item && typeof item === "object" ? item.id : item) === projectId;
  });
}

function updateProfileWidgets() {
  var pointsEl = document.getElementById("progress-points");
  var meterFill = document.getElementById("progress-meter-fill");
  var badgesEl = document.getElementById("progress-badges");
  var achievementList = document.getElementById("achievement-list");
  var leaderboardList = document.getElementById("leaderboard-list");
  var historyList = document.getElementById("completed-history-list");
  var completionBtn = document.getElementById("btn-mark-complete");

  // Individual activity counters (new HTML uses separate IDs)
  var searchesCount = document.getElementById("searches-count");
  var viewedCount = document.getElementById("projects-viewed-count");
  var codeCount = document.getElementById("code-opens-count");
  var completedCount = document.getElementById("projects-completed-count");

  if (pointsEl) pointsEl.textContent = progress.points;
  if (searchesCount) searchesCount.textContent = progress.searches;
  if (viewedCount) viewedCount.textContent = progress.projectViews;
  if (codeCount) codeCount.textContent = progress.codeOpens;
  if (completedCount) completedCount.textContent = progress.completions;

  if (meterFill) {
    var pct = Math.min(
      100,
      Math.round((progress.points / PROGRESS_MAX_POINTS) * 100),
    );
    meterFill.style.width = pct + "%";
    meterFill.setAttribute("aria-valuenow", String(pct));
    meterFill.textContent = pct + "%";
  }

  if (badgesEl) {
    var badgeDefs = [
      ["first_search", "First Search"],
      ["project_explorer", "Project Explorer"],
      ["code_starter", "Code Starter"],
      ["completionist", "Completionist"],
      ["roadmap_runner", "Roadmap Runner"],
    ];
    badgesEl.innerHTML = badgeDefs
      .map(function (b) {
        var unlocked = progress.badges[b[0]];
        return (
          '<li class="progress-badge ' +
          (unlocked ? "progress-badge--unlocked" : "progress-badge--locked") +
          '">' +
          '<span class="badge-icon">' +
          (unlocked ? "✓" : "★") +
          "</span>" +
          "<span>" +
          b[1] +
          "</span></li>"
        );
      })
      .join("");
  }

  if (achievementList) {
    achievementList.innerHTML = progress.achievements.length
      ? progress.achievements
          .map(function (a) {
            return (
              '<li class="achievement-item"><strong>' +
              a.title +
              "</strong>" +
              "<span>" +
              a.description +
              "</span><small>" +
              a.date +
              "</small></li>"
            );
          })
          .join("")
      : '<li class="achievement-empty">No achievements yet. Use DevPath and unlock the first badge.</li>';
  }

  if (leaderboardList) {
    var entries = [
      { name: "Ava", points: 245 },
      { name: "Kai", points: 192 },
      { name: "Sam", points: 176 },
      { name: "You", points: progress.points },
    ].sort(function (a, b) {
      return b.points - a.points;
    });
    leaderboardList.innerHTML = entries
      .map(function (e, i) {
        return (
          "<li><span>" +
          (i + 1) +
          ". " +
          e.name +
          "</span><strong>" +
          e.points +
          " pts</strong></li>"
        );
      })
      .join("");
  }

  if (historyList) {
    if (progress.completedProjects.length) {
      historyList.innerHTML = progress.completedProjects
        .slice(0, 5)
        .map(function (item) {
          var t =
            item && typeof item === "object" ? item.title : "Project " + item;
          return "<li><span>" + t + "</span><strong>Completed</strong></li>";
        })
        .join("");
    }
    // If empty, leave the HTML default empty state in place
  }

  if (completionBtn && typeof PROJECT_ID !== "undefined") {
    var done = projectIsCompleted(PROJECT_ID);
    completionBtn.textContent = done
      ? "Project Completed"
      : "Mark Project Complete";
    completionBtn.disabled = done;
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
    title: projectTitle || "Project " + projectId,
  });
  progress.completions = progress.completedProjects.length;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

loadProgressState();
updateProfileWidgets();


function escHtml(s) {
  return String(s || "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function aiStarterFilename(skills) {
  var l = (skills[0] || "").toLowerCase();
  if (l.includes("python") || l.includes("flask") || l.includes("django") || l.includes("fastapi")) return "main.py";
  if (l.includes("javascript") || l.includes("node") || l.includes("express")) return "index.js";
  if (l.includes("typescript") || l.includes("next") || l.includes("angular")) return "index.ts";
  if (l.includes("react")) return "App.jsx";
  if (l.includes("java")) return "Main.java";
  if (l.includes("kotlin")) return "Main.kt";
  if (l.includes("go")) return "main.go";
  if (l.includes("rust")) return "main.rs";
  if (l.includes("c++") || l.includes("cpp")) return "main.cpp";
  if (l.includes("c#")) return "Program.cs";
  return "main.py";
}

function aiStarterCode(project, skills) {
  var title  = project.title || "Project";
  var desc   = project.description || "";
  var l      = (skills[0] || "python").toLowerCase();

  if (l.includes("react") || l.includes("next")) return [
    "// " + title,
    "// " + desc.slice(0, 60),
    "",
    "import React, { useState, useEffect } from 'react';",
    "",
    "export default function App() {",
    "  const [data, setData] = useState([]);",
    "",
    "  useEffect(() => {",
    "    // TODO: fetch or initialise your data here",
    "  }, []);",
    "",
    "  return (",
    "    <div className=\"container\">",
    "      <h1>" + escHtml(title) + "</h1>",
    "      {/* TODO: build your UI here */}",
    "    </div>",
    "  );",
    "}"
  ].join("\n");

  if (l.includes("javascript") || l.includes("node") || l.includes("express")) return [
    "// " + title,
    "// " + desc.slice(0, 60),
    "",
    "const express = require('express');",
    "const app     = express();",
    "app.use(express.json());",
    "",
    "// GET /",
    "app.get('/', (req, res) => {",
    "  res.json({ message: 'Welcome to " + title + "' });",
    "});",
    "",
    "// TODO: add your routes below",
    "",
    "const PORT = process.env.PORT || 3000;",
    "app.listen(PORT, () =>",
    "  console.log('Server on http://localhost:' + PORT)",
    ");"
  ].join("\n");

  if (l.includes("typescript")) return [
    "// " + title,
    "",
    "interface Item {",
    "  id: number;",
    "  name: string;",
    "}",
    "",
    "function main(): void {",
    "  console.log('" + title + " — starting...');",
    "  // TODO: implement your logic",
    "}",
    "",
    "main();"
  ].join("\n");

  if (l.includes("java")) return [
    "// " + title,
    "",
    "public class Main {",
    "    public static void main(String[] args) {",
    "        System.out.println(\"" + title + " — starting...\");",
    "        // TODO: implement your logic here",
    "    }",
    "}"
  ].join("\n");

  if (l.includes("kotlin")) return [
    "// " + title,
    "",
    "fun main() {",
    "    println(\"" + title + " — starting...\")",
    "    // TODO: implement your logic here",
    "}"
  ].join("\n");

  if (l.includes("go")) return [
    "// " + title,
    "",
    "package main",
    "",
    "import \"fmt\"",
    "",
    "func main() {",
    "    fmt.Println(\"" + title + " — starting...\")",
    "    // TODO: implement your logic here",
    "}"
  ].join("\n");

  if (l.includes("rust")) return [
    "// " + title,
    "",
    "fn main() {",
    "    println!(\"" + title + " — starting...\");",
    "    // TODO: implement your logic here",
    "}"
  ].join("\n");

  if (l.includes("c++") || l.includes("cpp")) return [
    "// " + title,
    "",
    "#include <iostream>",
    "using namespace std;",
    "",
    "int main() {",
    "    cout << \"" + title + " — starting...\" << endl;",
    "    // TODO: implement your logic here",
    "    return 0;",
    "}"
  ].join("\n");

  
  return [
    "# " + title,
    "# " + desc.slice(0, 60),
    "",
    "def main():",
    "    print(\"" + title + " — starting...\")",
    "    # TODO: implement your logic here",
    "",
    "",
    "if __name__ == \"__main__\":",
    "    main()"
  ].join("\n");
}

function openAiProjectModal(project) {
  var old = document.getElementById("ai-project-modal-overlay");
  if (old) old.remove();

  var skills   = project.skills || project.tech_stack || [];
  var filename = aiStarterFilename(skills);
  var code     = aiStarterCode(project, skills);

  // Build badge HTML 
  var badgeHtml = "";
  if (project.level) {
    badgeHtml += '<span class="badge badge--' + project.level.toLowerCase() + '">' + escHtml(project.level) + '</span>';
  }
  if (project.interest) {
    badgeHtml += '<span class="badge badge--' + project.interest.toLowerCase() + '">' + escHtml(project.interest) + '</span>';
  }
  skills.forEach(function(s) {
    badgeHtml += '<span class="badge badge--' + s.toLowerCase().replace(/[^a-z0-9]/g,"-") + '">' + escHtml(s) + '</span>';
  });
  if (project.time) {
    badgeHtml += '<span class="badge badge--time">' + escHtml(project.time) + ' effort</span>';
  }

  // Tech stack tags 
  var techHtml = "";
  skills.forEach(function(s) {
    techHtml += '<span class="tech-tag">' + escHtml(s) + '</span>';
  });

  // Features list
  var featuresHtml = "";
  if (project.features && project.features.length) {
    project.features.forEach(function(f) {
      featuresHtml +=
        '<li class="feature-list-item">' +
          '<span class="feature-check">' +
            '<svg aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">' +
              '<polyline points="20 6 9 17 4 12"/>' +
            '</svg>' +
          '</span>' +
          escHtml(f) +
        '</li>';
    });
    featuresHtml = '<ul class="feature-list">' + featuresHtml + '</ul>';
  }

  // Roadmap steps
  var roadmapHtml = "";
  if (project.roadmap && project.roadmap.length) {
    project.roadmap.forEach(function(step, i) {
      roadmapHtml +=
        '<li class="roadmap-step">' +
          '<div class="roadmap-marker">' +
            '<span class="roadmap-dot"></span>' +
            '<span class="roadmap-line"></span>' +
          '</div>' +
          '<div class="roadmap-content">' +
            '<label class="roadmap-step-label">' +
              '<div class="roadmap-text-wrap">' +
                '<span class="roadmap-step-num">Step ' + (i + 1) + '</span>' +
                '<p class="roadmap-step-text">' + escHtml(step) + '</p>' +
              '</div>' +
            '</label>' +
          '</div>' +
        '</li>';
    });
    roadmapHtml =
      '<ol class="roadmap-timeline">' + roadmapHtml + '</ol>';
  }

  // Code lines 
  var codeLines = "";
  code.split("\n").forEach(function(line, i) {
    codeLines +=
      '<div class="code-line">' +
        '<span class="code-line-number" aria-hidden="true">' + (i + 1) + '</span>' +
        '<span class="code-line-content">' + escHtml(line) + '</span>' +
      '</div>';
  });

  // Outer overlay
  var overlay = document.createElement("div");
  overlay.id = "ai-project-modal-overlay";
  overlay.className = "code-panel-overlay";
  overlay.style.cssText =
    "display:flex;align-items:flex-start;justify-content:center;" +
    "overflow-y:auto;padding:40px 16px;z-index:500;";

  overlay.innerHTML = [
    
    '<div style="width:100%;max-width:900px;background:var(--surface,#fff);',
         'border-radius:var(--r-lg,12px);overflow:hidden;',
         'box-shadow:0 20px 60px rgba(0,0,0,0.18);">',

     
      '<div class="detail-hero" style="border-radius:0;margin:0;">',
        '<div style="padding:1.5rem 2rem;">',

         
          '<p style="font-size:0.75rem;opacity:0.7;margin:0 0 0.5rem;">',
            'AI Generated Project',
          '</p>',

          '<h1 class="detail-title" style="font-size:1.6rem;margin:0 0 1rem;">',
            escHtml(project.title),
          '</h1>',

          '<div class="badge-group">', badgeHtml, '</div>',

          '<p class="detail-description" style="margin-top:1rem;">',
            escHtml(project.description || ""),
          '</p>',

        '</div>',
      '</div>',

      
      '<div style="padding:2rem;display:grid;grid-template-columns:1fr 260px;',
           'gap:2rem;align-items:start;">',

        
        '<div>',

          
          project.features && project.features.length
            ? '<section class="detail-section">' +
                '<div class="detail-section-header">' +
                  '<div class="detail-section-icon">' +
                    '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                      '<polyline points="9 11 12 14 22 4"/>' +
                      '<path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>' +
                    '</svg>' +
                  '</div>' +
                  '<h2>Features</h2>' +
                '</div>' +
                featuresHtml +
              '</section>'
            : "",

          
          project.roadmap && project.roadmap.length
            ? '<section class="detail-section">' +
                '<div class="detail-section-header">' +
                  '<div class="detail-section-icon">' +
                    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                      '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>' +
                    '</svg>' +
                  '</div>' +
                  '<h2>Project Roadmap</h2>' +
                '</div>' +
                '<p class="detail-section-sub">Follow these steps in order. Each one builds on the previous.</p>' +
                roadmapHtml +
              '</section>'
            : "",

          
          '<section class="detail-section">',
            '<div class="detail-section-header">',
              '<div class="detail-section-icon">',
                '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
                  '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
                '</svg>',
              '</div>',
              '<h2>Starter Code</h2>',
            '</div>',

           
            '<div class="code-panel-header" style="position:relative;border-radius:var(--r-md,8px) var(--r-md,8px) 0 0;">',
              '<div class="code-panel-title">',
                '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
                  '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
                '</svg>',
                '<span>' + escHtml(filename) + '</span>',
              '</div>',
              '<div class="code-panel-actions">',
                '<button id="ai-modal-copy-btn" class="btn-copy-code" aria-label="Copy code">',
                  '<svg class="copy-icon" aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">',
                    '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>',
                    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
                  '</svg>',
                  '<span class="copy-btn-label">Copy Code</span>',
                '</button>',
              '</div>',
            '</div>',

            
            '<pre class="code-viewer" style="border-radius:0 0 var(--r-md,8px) var(--r-md,8px);max-height:380px;overflow-y:auto;margin:0;">',
              '<code id="ai-modal-code-content" style="display:block;">',
                codeLines,
              '</code>',
            '</pre>',
          '</section>',

        '</div>',

        
        '<aside class="detail-sidebar" style="position:sticky;top:20px;">',

         
          '<div class="sidebar-card">',
            '<h3 class="sidebar-card-title">',
              '<svg aria-hidden="true" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">',
                '<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>',
                '<line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
              '</svg>',
              'Tech Stack',
            '</h3>',
            '<div class="tech-tags">', techHtml, '</div>',
          '</div>',

         
          '<div class="sidebar-card">',
            '<h3 class="sidebar-card-title">',
              '<svg aria-hidden="true" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">',
                '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
              '</svg>',
              'Project Details',
            '</h3>',
            '<ul class="stats-list">',
              '<li><span class="stats-label">Difficulty</span>',
                '<span class="stats-value stats-value--' + (project.level || "").toLowerCase() + '">' + escHtml(project.level || "—") + '</span></li>',
              '<li><span class="stats-label">Interest</span>',
                '<span class="stats-value">' + escHtml(project.interest || "—") + '</span></li>',
              '<li><span class="stats-label">Effort</span>',
                '<span class="stats-value">' + escHtml(project.time || "—") + '</span></li>',
              project.roadmap
                ? '<li><span class="stats-label">Roadmap Steps</span><span class="stats-value">' + project.roadmap.length + ' steps</span></li>'
                : "",
            '</ul>',
          '</div>',

        '</aside>',

      '</div>',

     
      '<div style="padding:1rem 2rem 1.5rem;border-top:1px solid var(--border,#e5e7eb);',
           'display:flex;justify-content:flex-end;">',
        '<button id="ai-modal-close-btn" class="btn-view-code-sm"',
          ' style="border-color:var(--border);color:var(--text-body);">',
          'Close',
        '</button>',
      '</div>',

    '</div>'
  ].join("");

  document.body.appendChild(overlay);

 
  document.getElementById("ai-modal-close-btn").addEventListener("click", function() {
    overlay.remove();
  });
  overlay.addEventListener("click", function(e) {
    if (e.target === overlay) overlay.remove();
  });
  document.addEventListener("keydown", function onKey(e) {
    if (e.key === "Escape") { overlay.remove(); document.removeEventListener("keydown", onKey); }
  });

  
  document.getElementById("ai-modal-copy-btn").addEventListener("click", function() {
    var contentEl = document.getElementById("ai-modal-code-content");
    var lines = Array.prototype.slice.call(contentEl.querySelectorAll(".code-line-content"));
    var text  = lines.map(function(l) { return l.textContent; }).join("\n");
    var btn   = this;
    var label = btn.querySelector(".copy-btn-label");
    function done() {
      if (label) label.textContent = "Copied!";
      setTimeout(function() { if (label) label.textContent = "Copy Code"; }, 2000);
    }
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(done);
    } else {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;top:-9999px";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch(err) {}
      document.body.removeChild(ta);
      done();
    }
  });
}

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
  var quickPickChips = Array.prototype.slice.call(
    document.querySelectorAll(".skill-chip"),
  );

  var selectedSkills = [];
  var availableSkills =
    typeof skills !== "undefined" && Array.isArray(skills)
      ? skills
          .map(function (s) {
            return s.label;
          })
          .filter(Boolean)
      : quickPickChips.map(function (c) {
          return c.getAttribute("data-skill");
        });

  var activeSuggestionIndex = -1;
  var visibleSuggestions = [];

  // ----------------------------------------------------------
  // Helpers
  // ----------------------------------------------------------
  function normalize(v) {
    return String(v || "")
      .trim()
      .toLowerCase();
  }

  function isSelected(skill) {
    return selectedSkills.some(function (s) {
      return normalize(s) === normalize(skill);
    });
  }

  function canonicalSkill(raw) {
    var trimmed = String(raw || "").trim();
    var match = availableSkills.find(function (s) {
      return normalize(s) === normalize(trimmed);
    });
    return match || trimmed;
  }

  function syncSkillsHiddenInput() {
    if (skillsHidden) skillsHidden.value = JSON.stringify(selectedSkills);
  }

  function updateQuickPickState() {
    quickPickChips.forEach(function (chip) {
      var active = isSelected(chip.getAttribute("data-skill"));
      chip.classList.toggle("active", active);
      chip.classList.toggle("selected", active);
      chip.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  // ----------------------------------------------------------
  // Chip rendering
  // ----------------------------------------------------------
  function renderSelectedChips() {
    if (!selectedChips) return;
    selectedChips.textContent = "";
    selectedSkills.forEach(function (skill) {
      var chip = document.createElement("span");
      chip.className = "skill-chip-selected";
      chip.appendChild(document.createTextNode(skill));
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "skill-chip-remove";
      btn.setAttribute("aria-label", "Remove " + skill);
      btn.textContent = "×";
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        removeSkill(skill);
      });
      chip.appendChild(btn);
      selectedChips.appendChild(chip);
    });
  }

  // ----------------------------------------------------------
  // Add / Remove skill
  // ----------------------------------------------------------
  window.addSkill = function (rawSkill) {
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
    selectedSkills = selectedSkills.filter(function (s) {
      return normalize(s) !== normalize(skill);
    });
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
  }

  // ----------------------------------------------------------
  // Suggestions dropdown
  // ----------------------------------------------------------
  function hideSuggestions() {
    visibleSuggestions = [];
    activeSuggestionIndex = -1;
    if (suggestions) {
      suggestions.style.display = "none";
      suggestions.textContent = "";
    }
    if (skillsInput) skillsInput.setAttribute("aria-expanded", "false");
  }

  function filteredSkills(query) {
    var q = normalize(query);
    if (!q) return [];
    return availableSkills
      .filter(function (s) {
        return normalize(s).indexOf(q) !== -1 && !isSelected(s);
      })
      .slice(0, 8);
  }

  function renderSuggestionState() {
    if (!suggestions) return;
    suggestions
      .querySelectorAll(".suggestion-item")
      .forEach(function (item, i) {
        item.classList.toggle(
          "suggestion-item--active",
          i === activeSuggestionIndex,
        );
        item.setAttribute(
          "aria-selected",
          i === activeSuggestionIndex ? "true" : "false",
        );
      });
  }

  function showSuggestions(items) {
    visibleSuggestions = items;
    activeSuggestionIndex = -1;
    if (!suggestions) return;
    suggestions.textContent = "";
    if (!items.length) {
      hideSuggestions();
      return;
    }
    items.forEach(function (skill, i) {
      var item = document.createElement("div");
      item.className = "suggestion-item";
      item.id = "skills-suggestion-" + i;
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", "false");
      item.textContent = skill;
      item.addEventListener("mousedown", function (e) {
        e.preventDefault();
      });
      item.addEventListener("mouseenter", function () {
        activeSuggestionIndex = i;
        renderSuggestionState();
      });
      item.addEventListener("click", function () {
        window.addSkill(skill);
        if (skillsInput) skillsInput.value = "";
        hideSuggestions();
      });
      suggestions.appendChild(item);
    });
    suggestions.style.display = "block";
    skillsInput.setAttribute("aria-expanded", "true");
  }

  // ----------------------------------------------------------
  // Skill input listeners
  // ----------------------------------------------------------
  if (skillsInput) {
    skillsInput.addEventListener("input", function () {
      showSuggestions(filteredSkills(skillsInput.value));
    });
    skillsInput.addEventListener("focus", function () {
      if (skillsInput.value.trim())
        showSuggestions(filteredSkills(skillsInput.value));
    });
    skillsInput.addEventListener("blur", function () {
      window.setTimeout(hideSuggestions, 150);
    });
    skillsInput.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        if (!visibleSuggestions.length)
          showSuggestions(filteredSkills(skillsInput.value));
        if (!visibleSuggestions.length) return;
        e.preventDefault();
        activeSuggestionIndex =
          e.key === "ArrowDown"
            ? (activeSuggestionIndex + 1) % visibleSuggestions.length
            : activeSuggestionIndex <= 0
              ? visibleSuggestions.length - 1
              : activeSuggestionIndex - 1;
        renderSuggestionState();
        return;
      }
      if (e.key === "Escape") {
        hideSuggestions();
        return;
      }
      if (e.key === "Enter") {
        e.preventDefault();
        if (
          activeSuggestionIndex >= 0 &&
          visibleSuggestions[activeSuggestionIndex]
        ) {
          window.addSkill(visibleSuggestions[activeSuggestionIndex]);
          skillsInput.value = "";
          hideSuggestions();
          return;
        }
        if (skillsInput.value.trim()) {
          window.addSkill(skillsInput.value);
          skillsInput.value = "";
        }
        hideSuggestions();
      }
    });
  }

  // Dropdown toggle button
  var dropdownBtn = document.getElementById("skills-dropdown-toggle");
  if (dropdownBtn && suggestions) {
    dropdownBtn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (suggestions.style.display === "block") {
        hideSuggestions();
      } else {
        showSuggestions(
          availableSkills
            .filter(function (s) {
              return !isSelected(s);
            })
            .slice(0, 30),
        );
      }
    });
  }

  // Quick-pick chips
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");
      if (!skill) return;
      if (isSelected(skill)) removeSkill(skill);
      else window.addSkill(skill);
      if (skillsInput) skillsInput.value = "";
      hideSuggestions();
    });
  });

  // Click outside closes suggestions
  document.addEventListener("click", function (e) {
    if (skillWrap && !skillWrap.contains(e.target)) hideSuggestions();
  });

  // Focus chip wrap → focus input
  if (skillWrap) {
    skillWrap.style.position = "relative"; 
    skillWrap.addEventListener("click", function () {
      if (skillsInput) skillsInput.focus();
    });
  }

  // ----------------------------------------------------------
  // Form validation
  // ----------------------------------------------------------
  function showFieldError(id, msg) {
    var el = document.getElementById(id);
    if (el) el.textContent = msg;
  }
  function clearFieldError(id) {
    var el = document.getElementById(id);
    if (el) el.textContent = "";
  }
  function clearAllErrors() {
    ["skills-error", "level-error", "interest-error", "time-error"].forEach(
      clearFieldError,
    );
    var g = document.getElementById("form-error-general");
    if (g) g.textContent = "";
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
    if (submitBtn) {
      submitBtn.disabled = isLoading;
      submitBtn.setAttribute("aria-busy", isLoading ? "true" : "false");
    }
    if (btnLabel) btnLabel.style.display = isLoading ? "none" : "inline";
    if (btnLoading)
      btnLoading.style.display = isLoading ? "inline-flex" : "none";
    if (resultsSection) {
      resultsSection.style.display = "block";
      if (isLoading) {
        if (resultsLoadingEl) resultsLoadingEl.style.display = "block";
        if (resultsGrid) resultsGrid.style.display = "none";
        if (resultsEmptyEl) resultsEmptyEl.style.display = "none";
        resultsSection.scrollIntoView({ behavior: "smooth" });
      } else {
        if (resultsLoadingEl) resultsLoadingEl.style.display = "none";
      }
    }
  }

  // ----------------------------------------------------------
  // Result card rendering
  // ----------------------------------------------------------
  function truncate(text, max) {
    if (!text) return "";
    return text.length > max ? text.slice(0, max) + "..." : text;
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
        descText.textContent = expanded
          ? project.description
          : truncate(project.description, 120);
        readMore.textContent = expanded ? "Read less" : "Read more";
        readMore.setAttribute("aria-expanded", expanded ? "true" : "false");
      });
      desc.appendChild(readMore);
    }

    var tags = document.createElement("div");
    tags.className = "project-card-tags";
    (project.skills || []).forEach(function (s) {
      tags.appendChild(createTag(s, "skill"));
    });
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
    if (String(project.id).startsWith("ai-")) {
      link.href = "#";
      link.addEventListener("click", function (e) {
        e.preventDefault();
        openAiProjectModal(project);
      });
    } else {
      link.href = "/project/" + project.id;
    }
    footer.appendChild(link);
    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tags);
    card.appendChild(footer);
    return card;
  }

  function renderResults(projects, message) {
    if (!resultsSection) return;

    projects = Array.isArray(projects) ? projects : [];

    resultsSection.style.display = "block";

    if (resultsLoadingEl) resultsLoadingEl.style.display = "none";
    if (resultsGrid) resultsGrid.innerHTML = "";

    var shareWrap = document.getElementById("share-result-wrap");
    var hasResults = projects.length > 0;

    if (resultsGrid) resultsGrid.style.display = hasResults ? "grid" : "none";
    if (resultsEmptyEl)
      resultsEmptyEl.style.display = hasResults ? "none" : "block";
    if (shareWrap) shareWrap.style.display = hasResults ? "flex" : "none";

    if (!hasResults) {
      var emptyEl = document.getElementById("empty-message");
      if (emptyEl) emptyEl.textContent = message || "No projects found.";

      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    projects.forEach(function (p) {
      resultsGrid.appendChild(buildProjectCard(p));
    });

    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  // ----------------------------------------------------------
  // Share URL
  // ----------------------------------------------------------
  var MAX_SHARE_SKILLS = 10;
  var MAX_URL_LENGTH = 2000;

  function buildShareUrl() {
    var baseUrl = window.location.origin + window.location.pathname;
    var params = new URLSearchParams();
    var allSkills = skillsHidden ? skillsHidden.value.trim() : "";
    var skillsArr = [];
    var truncatedFlag = false;

    if (allSkills) {
      skillsArr = allSkills
        .split(",")
        .map(function (s) {
          return s.trim();
        })
        .filter(Boolean);
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
  var shareTOHandle = null;
  var _truncated = false;

  function showShareSuccess() {
    if (!shareBtn) return;
    var lbl = shareBtn.querySelector(".share-btn-label");
    if (lbl)
      lbl.textContent = _truncated
        ? "Copied! (some skills trimmed)"
        : "Copied!";
    shareBtn.classList.add("copied");
    if (shareToast) shareToast.classList.add("show");
    clearTimeout(shareTOHandle);
    shareTOHandle = setTimeout(function () {
      if (lbl) lbl.textContent = "Share My Result";
      shareBtn.classList.remove("copied");
      if (shareToast) shareToast.classList.remove("show");
    }, 2500);
  }

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.cssText = "position:fixed;top:-9999px;left:-9999px;opacity:0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      document.execCommand("copy");
      showShareSuccess();
    } catch (e) {}
    document.body.removeChild(ta);
  }

  if (shareBtn) {
    shareBtn.addEventListener("click", function () {
      var result = buildShareUrl();
      _truncated = result.truncated;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(result.url)
          .then(showShareSuccess)
          .catch(function () {
            fallbackCopy(result.url);
          });
      } else {
        fallbackCopy(result.url);
      }
    });
  }

  // ----------------------------------------------------------
  // Query param pre-fill from shared URL
  // ----------------------------------------------------------
  var VALID_LEVELS = ["Beginner", "Intermediate", "Advanced"];
  var VALID_INTERESTS = [
    "Web",
    "Data",
    "Education",
    "Automation",
    "Games",
    "Cybersecurity",
    "Devops",
    "Backend",
    "Tools",
    "Productivity",
    "Business Logic",
    "Mobile",
    "Machine Learning/AI",
  ];
  var VALID_TIMES = ["Low", "Medium", "High"];

  function sanitizeSkillValue(raw) {
    if (!raw || typeof raw !== "string") return "";
    return raw
      .replace(/<[^>]*>/g, "")
      .replace(/[^A-Za-z0-9 .#+_\-\/]/g, "")
      .trim();
  }

  function validateDropdownValue(value, list) {
    if (!value || typeof value !== "string") return "";
    var t = value.trim();
    for (var i = 0; i < list.length; i++) {
      if (list[i] === t) return t;
    }
    resultsEmptyEl.style.display = "none";
    resultsGrid.style.display = "grid";
    projects.forEach(function (project) { resultsGrid.appendChild(buildProjectCard(project)); });
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  (function initFromQueryParams() {
    var params = new URLSearchParams(window.location.search);
    var qSkills = params.get("skills");
    var qLevel = params.get("level");
    var qInterest = params.get("interest");
    var qTime = params.get("time");
    if (!qSkills || !qLevel || !qInterest || !qTime) return;

    var safeLevel = validateDropdownValue(qLevel, VALID_LEVELS);
    var safeInterest = validateDropdownValue(qInterest, VALID_INTERESTS);
    var safeTime = validateDropdownValue(qTime, VALID_TIMES);
    if (!safeLevel || !safeInterest || !safeTime) return;

    qSkills.split(",").forEach(function (s) {
      var safe = sanitizeSkillValue(s);
      if (safe) window.addSkill(safe);
    });
    document.getElementById("level").value = safeLevel;
    document.getElementById("interest").value = safeInterest;
    document.getElementById("time").value = safeTime;

    var banner = document.getElementById("share-prefill-banner");
    var bannerClose = document.getElementById("share-prefill-banner-close");
    if (banner) {
      banner.style.display = "flex";
      if (bannerClose)
        bannerClose.addEventListener("click", function () {
          banner.style.display = "none";
        });
      var formSection = document.getElementById("the-project");
      if (formSection) formSection.scrollIntoView({ behavior: "smooth" });
    }
  })();

  // ----------------------------------------------------------
  // Clear filters button
  // ----------------------------------------------------------
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
      if (resultsSection) resultsSection.style.display = "none";
      if (skillsInput) skillsInput.focus();
    });
  }

  // ----------------------------------------------------------
  // Reset progress button
  // ----------------------------------------------------------
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
        roadmap_runner: false,
      };
      saveProgressState();
      updateProfileWidgets();
      showAchievementToast(
        "Progress reset",
        "Your local profile has been cleared.",
      );
    });
  }

  // ----------------------------------------------------------
  // Form submission
  // ----------------------------------------------------------
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearAllErrors();
    if (skillsInput && skillsInput.value.trim()) {
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
      }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok)
            throw new Error(
              data.error || "Unable to generate recommendations.",
            );
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
        var g = document.getElementById("form-error-general");
        if (g)
          g.textContent =
            err.message || "An unexpected error occurred. Please try again.";
      });
  });

  // ----------------------------------------------------------
  // GitHub modal
  // ----------------------------------------------------------
  var githubModal = document.getElementById("github-modal-overlay");
  var openModalBtn = document.getElementById("btn-show-github");
  var closeModalBtn = document.getElementById("btn-close-github");
  var fetchBtn = document.getElementById("btn-fetch-github");
  var githubInput = document.getElementById("github-username");
  var githubErrorMsg = document.getElementById("github-modal-error");

  function closeGithubModal() {
    if (githubModal) githubModal.classList.remove("active");
    if (githubInput) githubInput.value = "";
    if (githubErrorMsg) githubErrorMsg.textContent = "";
  }

  if (
    githubModal &&
    openModalBtn &&
    closeModalBtn &&
    fetchBtn &&
    githubInput &&
    githubErrorMsg
  ) {
    openModalBtn.addEventListener("click", function () {
      githubModal.classList.add("active");
      githubInput.focus();
    });
    closeModalBtn.addEventListener("click", closeGithubModal);
    githubModal.addEventListener("click", function (e) {
      if (e.target === githubModal) closeGithubModal();
    });

    fetchBtn.addEventListener("click", function () {
      var username = githubInput.value.trim();
      githubErrorMsg.textContent = "";
      if (!username) {
        githubErrorMsg.textContent = "Please enter a GitHub username.";
        return;
      }
      fetchBtn.disabled = true;
      fetchBtn.textContent = "Syncing...";

      fetch(
        "https://api.github.com/users/" +
          encodeURIComponent(username) +
          "/repos?sort=updated&per_page=100",
      )
        .then(function (res) {
          if (!res.ok)
            throw new Error(
              res.status === 404
                ? "Username not found."
                : "Unable to fetch GitHub repositories.",
            );
          return res.json();
        })
        .then(function (repos) {
          var languages = [];
          repos.forEach(function (repo) {
            if (repo.language && languages.indexOf(repo.language) === -1)
              languages.push(repo.language);
          });
          if (!languages.length) {
            githubErrorMsg.textContent = "No public languages found.";
            return;
          }
          languages.forEach(window.addSkill);
          closeGithubModal();
        })
        .catch(function (err) {
          githubErrorMsg.textContent =
            err.name === "TypeError"
              ? "Network error: please check your connection or disable adblockers."
              : err.message || "Failed to fetch skills.";
          fetchBtn.disabled = false;
          fetchBtn.textContent = "Fetch Skills";
        });
    });
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
    if (!codeContentEl) return;
    codeContentEl.textContent = "";
    String(code || "")
      .split("\n")
      .forEach(function (line, i) {
        var row = document.createElement("div");
        row.className = "code-line";
        var number = document.createElement("span");
        number.className = "code-line-number";
        number.setAttribute("aria-hidden", "true");
        number.textContent = i + 1;
        var content = document.createElement("span");
        content.className = "code-line-content";
        content.textContent = line;
        row.appendChild(number);
        row.appendChild(content);
        codeContentEl.appendChild(row);
      });
  }

  function fetchStarterCode() {
    if (codeContentEl) codeContentEl.textContent = "Loading starter code...";
    fetch("/project/" + PROJECT_ID + "/code")
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok)
            throw new Error(data.error || "Starter code unavailable.");
          return data;
        });
      })
      .then(function (data) {
        if (codePanelFilename) codePanelFilename.textContent = data.filename;
        renderCode(data.code);
        codeFetched = true;
      })
      .catch(function (err) {
        if (codeContentEl)
          codeContentEl.textContent =
            err.message || "Could not load starter code.";
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
  if (codePanelOverlay)
    codePanelOverlay.addEventListener("click", closeCodePanel);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeCodePanel();
  });

  if (btnCopyCode) {
    btnCopyCode.addEventListener("click", function () {
      if (!codeContentEl) return;
      var code = Array.prototype.slice
        .call(codeContentEl.querySelectorAll(".code-line-content"))
        .map(function (l) {
          return l.textContent;
        })
        .join("\n");
      if (!code) return;
      var done = function () {
        if (copyToast) {
          copyToast.classList.add("show");
          window.setTimeout(function () {
            copyToast.classList.remove("show");
          }, 2500);
        }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = code;
        ta.style.cssText = "position:fixed;top:-9999px;left:-9999px";
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        try {
          document.execCommand("copy");
        } catch (e) {}
        document.body.removeChild(ta);
        done();
      }
    });
  }

  // Roadmap checkboxes
  var roadmapCheckboxes = Array.prototype.slice.call(
    document.querySelectorAll(".roadmap-checkbox"),
  );
  var progressFill = document.getElementById("roadmap-progress-fill");
  var progressText = document.getElementById("roadmap-progress-text");
  var progressBar = document.querySelector(".roadmap-progress-bar");
  var roadmapKey = "devpath-roadmap-progress-" + PROJECT_ID;

  function updateRoadmapProgress() {
    if (!roadmapCheckboxes.length) return;
    var done = roadmapCheckboxes.filter(function (c) {
      return c.checked;
    }).length;
    var pct = Math.round((done / roadmapCheckboxes.length) * 100);
    roadmapCheckboxes.forEach(function (c) {
      var step = c.closest(".roadmap-step");
      if (step) step.classList.toggle("completed", c.checked);
    });
    if (progressFill) progressFill.style.width = pct + "%";
    if (progressText) progressText.textContent = pct + "% completed";
    if (progressBar) progressBar.setAttribute("aria-valuenow", String(pct));
    try {
      localStorage.setItem(
        roadmapKey,
        JSON.stringify(
          roadmapCheckboxes.map(function (c) {
            return c.checked;
          }),
        ),
      );
    } catch (e) {}
  }

  try {
    var savedRoadmap = JSON.parse(localStorage.getItem(roadmapKey) || "[]");
    roadmapCheckboxes.forEach(function (c, i) {
      c.checked = !!savedRoadmap[i];
    });
  } catch (e) {}
  roadmapCheckboxes.forEach(function (c) {
    c.addEventListener("change", updateRoadmapProgress);
  });
  updateRoadmapProgress();

  if (completionBtn) {
    completionBtn.addEventListener("click", function () {
      recordCompletion(
        PROJECT_ID,
        typeof PROJECT_TITLE !== "undefined" ? PROJECT_TITLE : "",
      );
      showAchievementToast(
        "Project completed",
        "Nice work finishing this project.",
      );
    });
  }
})();

// ============================================================
// SCROLL-TO-TOP / SCROLL-TO-BOTTOM BUTTON
// ============================================================
(function initScrollButton() {
  var button = document.getElementById("scroll-top-btn");
  var icon = document.getElementById("scroll-btn-icon");
  if (!button) return;
  var atBottom = false;

  function nearBottom() {
    return (
      window.innerHeight + window.pageYOffset >= document.body.scrollHeight - 40
    );
  }

  function update() {
    button.classList.toggle("visible", window.pageYOffset > 200);
    atBottom = nearBottom();
    button.setAttribute(
      "aria-label",
      atBottom ? "Scroll to top" : "Scroll to bottom",
    );
    button.title = atBottom ? "Scroll to top" : "Scroll to bottom";
    if (icon)
      icon.innerHTML = atBottom
        ? '<polyline points="18 15 12 9 6 15"/>'
        : '<polyline points="6 9 12 15 18 9"/>';
  }

  window.addEventListener("scroll", update, { passive: true });
  button.addEventListener("click", function () {
    window.scrollTo({
      top: atBottom ? 0 : document.body.scrollHeight,
      behavior: "smooth",
    });
  });
  update();
})();
