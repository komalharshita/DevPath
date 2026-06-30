// DevPath client-side behavior.

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
  progress.points = progress.searches * 5 + progress.projectViews * 10 +
    progress.codeOpens * 15 + progress.completions * 30;
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
    var percentage = Math.min(100, Math.round((progress.points / 250) * 100));
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

  function getSavedProjects() {
    try {
      var saved = JSON.parse(localStorage.getItem(SAVED_PROJECTS_KEY) || "[]");
      return Array.isArray(saved) ? saved : [];
    } catch (err) {
      console.warn("Unable to load saved projects", err);
      return [];
    }
  }

  function saveSavedProjects(projects) {
    try {
      localStorage.setItem(SAVED_PROJECTS_KEY, JSON.stringify(projects));
    } catch (err) {
      console.warn("Unable to save projects", err);
    }
  }

  function projectIsSaved(projectId) {
    return getSavedProjects().some(function (project) {
      return String(project.id) === String(projectId);
    });
  }

  function saveProject(project) {
    var saved = getSavedProjects();
    if (saved.some(function (item) { return String(item.id) === String(project.id); })) return;

    saved.unshift({
      id: project.id,
      title: project.title,
      level: project.level || "",
      time: project.time || "",
      skills: Array.isArray(project.skills) ? project.skills.slice(0, 4) : []
    });
    saveSavedProjects(saved);
    renderSavedProjects();
  }

  function removeSavedProject(projectId) {
    var saved = getSavedProjects().filter(function (project) {
      return String(project.id) !== String(projectId);
    });
    saveSavedProjects(saved);
    renderSavedProjects();
    document.querySelectorAll("[data-save-project-id='" + projectId + "']").forEach(function (button) {
      button.classList.remove("saved");
      button.textContent = "Save Project";
      button.setAttribute("aria-pressed", "false");
    });
  }

  function toggleSavedProject(project, button) {
    if (projectIsSaved(project.id)) {
      removeSavedProject(project.id);
      return;
    }

    saveProject(project);
    button.classList.add("saved");
    button.textContent = "Saved";
    button.setAttribute("aria-pressed", "true");
  }

  function renderSavedProjects() {
    var list = document.getElementById("saved-projects-list");
    var count = document.getElementById("saved-projects-count");
    if (!list || !count) return;

    var saved = getSavedProjects();
    count.textContent = saved.length + " saved";
    list.textContent = "";

    if (!saved.length) {
      var empty = document.createElement("p");
      empty.className = "saved-projects-empty";
      empty.textContent = "No saved projects yet.";
      list.appendChild(empty);
      return;
    }

    saved.forEach(function (project) {
      var item = document.createElement("article");
      item.className = "saved-project-item";

      var title = document.createElement("a");
      title.href = "/project/" + project.id;
      title.textContent = project.title;

      var meta = document.createElement("span");
      meta.textContent = [project.level, project.time].filter(Boolean).join(" - ");

      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "saved-project-remove";
      remove.textContent = "Remove";
      remove.addEventListener("click", function () {
        removeSavedProject(project.id);
      });

      item.appendChild(title);
      item.appendChild(meta);
      item.appendChild(remove);
      list.appendChild(item);
    });
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

  function syncSkillsHiddenInput() {
    if (!skillsHidden){
      skillsHidden = document.getElementById("skills");
    }
    // Keep the hidden <input> in sync for form serialisation
    // The API expects a comma-separated string, so join the array that way
    skillsHidden.value = selectedSkills.join(", ");
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



  // ----------------------------------------------------------
  // Form submission and API call
  // ----------------------------------------------------------

  form.addEventListener("submit", function (evt) {
    evt.preventDefault(); //stop the browser from reloading the page on form submit
    clearAllErrors();

    if (skillsTextInput.value.trim()) {
      addSkill(skillsTextInput.value);
      skillsTextInput.value = "";
      hideSuggestions();
    }

    if (!validateForm()) return; //stop - anything missing/invalid

    setLoadingState(true);

    // Allow browser to paint spinner before request starts
    requestAnimationFrame(function () {

      //combine form values into an object to send to server/api
      var payload = {
        // Prefer the hidden input value; fall back to raw text box if hidden input is empty
        skills: skillsHidden.value.trim() || skillsTextInput.value.trim(),
        level: document.getElementById("level").value,
        interest: document.getElementById("interest").value,
        time: document.getElementById("time").value
      };

      //post the data to backend api as JSON, then handle the response
      fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload) //convert object to json string
      })
        .then(function (res) {
          return res.json(); //parse the response as JSON
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
        .catch(function (err) {
          // this runs if the network request itself fails
          setLoadingState(false);
          var generalErr = document.getElementById("form-error-general");
          if (generalErr) generalErr.textContent = "Something went wrong. Please try again.";
          console.error("API request failed:", err);
        });
    });
  });


  // Manages the loading state of the form and results section(whats visible or not)
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
      resultsGrid.style.display = "grid"; //switch back to grid layout
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

    if (!projects || projects.length === 0) { //if no projects returned from api, show the "no results" message and hide the grid
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";

      var interestEl = document.getElementById("interest");
      var selectedInterest = interestEl ? interestEl.value : null;

      // Show a friendly custom message when the user selected an interest
      if (emptyMessageEl) {
        if (selectedInterest) {
          emptyMessageEl.textContent = "No projects are currently available for this interest. Please check back later or try a different area.";
        } else if (message) {
          emptyMessageEl.textContent = message;
        } else {
          emptyMessageEl.textContent = "Try adjusting your skills or choosing a different interest area.";
        }
      }

      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    resultsEmptyEl.style.display = "none";
    resultsGrid.style.display = "grid";

    //build a card for each project and add it to the grid
    projects.forEach(function (project) {
      resultsGrid.appendChild(buildProjectCard(project));
    });

    resultsSection.scrollIntoView({ behavior: "smooth" });
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

    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;  // display the project name as the card heading

    // -----------------------------------------------------------------------
    // CHANGE: Score Badge — displays "Match Score X.X / 10" on the project card
    // REASON: The issue asked for a score out of 10 next to each recommended
    //         project so users can instantly see how well it matches their input.
    //         The score value comes from the API response field "match_score"
    //         that was added to utils/recommender.py.
    // -----------------------------------------------------------------------
    if (typeof project.match_score === "number") {
      // REASON: Only build the badge if the API actually returned a match_score.
      //         This makes the code safe — if the field is missing for any reason,
      //         the card still renders normally without crashing.

      // Create the outer container div that holds the label, number, and bar
      var scoreBadge = document.createElement("div");
      scoreBadge.className = "project-match-score"; // CSS class defined in style.css for layout/spacing
      // REASON: aria-label makes the score readable by screen readers (accessibility)
      scoreBadge.setAttribute("aria-label", "Match score: " + project.match_score + " out of 10");

      // Create the "Match Score" text label shown on the left side of the badge
      var scoreLabel = document.createElement("span");
      scoreLabel.className = "score-label"; // styled as semi-bold gray text in CSS
      scoreLabel.textContent = "Match Score"; // static label text the user sees

      // Create the numeric score display e.g. "3.8 / 10"
      var scoreValue = document.createElement("span");
      scoreValue.className = "score-value"; // styled as bold accent-color text in CSS
      // REASON: toFixed(1) ensures exactly 1 decimal place e.g. "3.8" not "3.800000"
      scoreValue.textContent = project.match_score.toFixed(1) + " / 10";

      // Create the outer track (gray background bar) for the visual progress bar
      var scoreBar = document.createElement("div");
      scoreBar.className = "score-bar"; // thin gray background track styled in CSS
      // REASON: role="presentation" tells screen readers to ignore the bar
      //         since the aria-label on the badge already conveys the information
      scoreBar.setAttribute("role", "presentation");

      // Create the colored fill that sits inside the bar track
      var scoreBarFill = document.createElement("div");
      scoreBarFill.className = "score-bar-fill"; // accent-colored fill styled in CSS
      // REASON: match_score is 0–10, so multiplying by 10 converts it to a 0–100%
      //         width. Example: score 3.8 → width 38%, score 10 → width 100%
      scoreBarFill.style.width = (project.match_score * 10) + "%";

      // Assemble the elements: fill goes inside bar track
      scoreBar.appendChild(scoreBarFill);
      // Then add label, number, and bar into the badge container
      scoreBadge.appendChild(scoreLabel);
      scoreBadge.appendChild(scoreValue);
      scoreBadge.appendChild(scoreBar);
      // REASON: Inject the badge into the card between the title and description
      //         so the score is visible immediately without scrolling
      card.appendChild(scoreBadge);
    }
    // -----------------------------------------------------------------------
    // END of Score Badge change
    // -----------------------------------------------------------------------

    if (project.match_explanation) {
      var explanationP = document.createElement("p");
      explanationP.className = "project-match-explanation";
      explanationP.innerHTML = '<svg class="explanation-icon" aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><span>' + project.match_explanation + '</span>';
      card.appendChild(explanationP);
    }

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

    var saveButton = document.createElement("button");
    saveButton.type = "button";
    saveButton.className = "btn-save-project";
    saveButton.setAttribute("data-save-project-id", project.id);
    saveButton.setAttribute("aria-pressed", projectIsSaved(project.id) ? "true" : "false");
    if (projectIsSaved(project.id)) {
      saveButton.classList.add("saved");
      saveButton.textContent = "Saved";
    } else {
      saveButton.textContent = "Save Project";
    }
    saveButton.addEventListener("click", function () {
      toggleSavedProject(project, saveButton);
    });

    var link = document.createElement("a");
    link.className = "btn-details";
    link.textContent = "View Full Project";
    link.href = "/project/" + project.id;
    link.addEventListener("click", function() {
        if (project.match_explanation) {
            sessionStorage.setItem("project_" + project.id + "_explanation", project.match_explanation);
        }
    });
    footer.appendChild(saveButton);
    footer.appendChild(link);

    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tags);
    card.appendChild(footer);
    return card;
  }

  renderSavedProjects();


  function runProjectSearch(query) {
    if (!query) return;
    setLoadingState(true);
    fetch("/api/search?q=" + encodeURIComponent(query))
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error("Search failed. Please try again.");
          return data;
        });
      })
      .then(function (projects) {
        setLoadingState(false);
        recordSearch();
        var message = projects.length
          ? null
          : "No projects matched \"" + query + "\". Try a different keyword.";
        renderResults(projects, message);
        var mobileMenu = document.getElementById("nav-mobile-menu");
        var mobileToggle = document.getElementById("nav-mobile-toggle");
        if (mobileMenu && mobileMenu.classList.contains("open")) {
          mobileMenu.classList.remove("open");
          if (mobileToggle) {
            mobileToggle.classList.remove("open");
            mobileToggle.setAttribute("aria-expanded", "false");
          }
        }
      })
      .catch(function (err) {
        setLoadingState(false);
        var general = document.getElementById("form-error-general");
        if (general) general.textContent = err.message || "Search failed. Please try again.";
      });
  }

  function bindSearchForm(form, input) {
    if (!form || !input) return;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      runProjectSearch(input.value.trim());
    });
  }

  bindSearchForm(document.getElementById("topic-search-form"), document.getElementById("topic-search"));
  bindSearchForm(document.getElementById("topic-search-form-mobile"), document.getElementById("topic-search-mobile"));

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
  });

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
  openModalBtn.focus(); // add this line
}

  if (modal && openModalBtn && closeModalBtn && fetchBtn && githubInput && errorMsg) {
    openModalBtn.addEventListener("click", function () {
      modal.classList.add("active");
      githubInput.focus();
    });
    modal.addEventListener("keydown", function (event) {
  if (!modal.classList.contains("active")) return;
  var focusable = modal.querySelectorAll("button, input");
  var first = focusable[0];
  var last = focusable[focusable.length - 1];
  if (event.key === "Tab") {
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
  if (event.key === "Escape") closeGithubModal();
});
    closeModalBtn.addEventListener("click", closeGithubModal);
    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeGithubModal();
    });
    fetchBtn.addEventListener("click", function () {
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
          errorMsg.textContent = err.message || "Failed to fetch skills.";
        })
        .finally(function () {
          fetchBtn.disabled = false;
          fetchBtn.textContent = "Fetch Skills";
        });
    });
  }
})();

(function initDetailPage() {
  if (typeof PROJECT_ID === "undefined") return;
  recordProjectView();

  var matchExplanationContainer = document.getElementById("project-match-explanation-container");
  var savedExplanation = sessionStorage.getItem("project_" + PROJECT_ID + "_explanation");
  if (matchExplanationContainer && savedExplanation) {
      matchExplanationContainer.innerHTML = '<p class="project-match-explanation detail-explanation"><svg class="explanation-icon" aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><span>' + savedExplanation + '</span></p>';
  }

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
