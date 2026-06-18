// script.js — DevPath client-side logic
//
// Responsibilities:
//   - Mobile navigation toggle
//   - Skill chip manager (add/remove skills)
//   - Form validation with per-field error messages
//   - Recommendation API call and loading states
//   - Result card rendering
//   - Code viewer panel (detail page)

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
    // Keep aria-expanded in sync so screen readers know if menu is open or closed
    toggle.setAttribute("aria-expanded", isOpen);
  });

  // Close menu when any mobile link is clicked
  menu.querySelectorAll(".nav-mobile-link").forEach(function (link) { 
    link.addEventListener("click", function () { 
      menu.classList.remove("open"); 
      toggle.classList.remove("open");
    });
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

function computeProgressPoints() {
  var raw =
    progress.searches      * POINTS_PER_SEARCH     +
    progress.projectViews  * POINTS_PER_VIEW       +
    progress.codeOpens     * POINTS_PER_CODE_OPEN  +
    progress.completions   * POINTS_PER_COMPLETION;
  // Clamp stored points so they never exceed max — prevents aria-valuenow > 100
  progress.points = Math.min(raw, PROGRESS_MAX_POINTS);
}

  // Clear Filters Button Functionality
  var clearFiltersBtn = document.getElementById("clear-filters-btn");
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function () {
      var recommendForm = document.getElementById("recommend-form");
      if (recommendForm) {
        recommendForm.reset();
        resetSkillSelection();
        if (skillsTextInput) skillsTextInput.focus();
      }
    });
  }

  // Also reset skills when the native form reset event fires
  form.addEventListener("reset", function () {
    window.setTimeout(function () {
      resetSkillSelection();
      if (skillsTextInput) skillsTextInput.focus();
    }, 0);
  });


  // ----------------------------------------------------------
  // Skill chip manager
  // ----------------------------------------------------------

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
    var percentage = Math.min(
      100,
      Math.round((progress.points / PROGRESS_MAX_POINTS) * 100)
    );
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
  }
}


function recordSearch() {
  progress.searches += 1;
  computeProgressPoints();
  tryUnlockBadges();
  saveProgressState();
  updateProfileWidgets();
}

  var suggestionsDiv         = document.getElementById("skills-suggestions");
  var skillWrap              = document.getElementById("skill-input-wrap");
  var visibleSuggestions     = [];
  var activeSuggestionIndex  = -1;

  // Deduplicate available skills (case-insensitive)
  availableSkills = availableSkills.filter(function (skill, index, list) {
    return typeof skill === "string" && skill.trim() &&
      list.findIndex(function (item) {
        return item.toLowerCase() === skill.toLowerCase();
      }) === index;
  });

  if (suggestionsDiv) suggestionsDiv.setAttribute("role", "listbox");

  function normalizeSkill(skill) { return skill.trim().toLowerCase(); }

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

  function normalize(value) {
    return String(value || "").trim().toLowerCase();
  }

  function getCanonicalSkill(rawSkill) {
    var normalizedSkill = normalizeSkill(rawSkill);
    var matched = availableSkills.find(function (s) { return normalizeSkill(s) === normalizedSkill; });
    return matched || rawSkill.trim();
  }

  function getFilteredSkills(query) {
    var normalizedQuery = normalizeSkill(query);
    return availableSkills.filter(function (skill) {
      return normalizeSkill(skill).includes(normalizedQuery) && !isSkillSelected(skill);
    }).slice(0, 8);
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
    visibleSuggestions     = [];
    activeSuggestionIndex  = -1;
    if (suggestionsDiv) { suggestionsDiv.style.display = "none"; suggestionsDiv.innerHTML = ""; }
  }

  function selectSuggestion(skill) {
    addSkill(skill);
    skillsTextInput.value = "";
    hideSuggestions();
    skillsTextInput.focus();
  }

  function displaySuggestions(items) {
    if (!suggestionsDiv) return;
    visibleSuggestions    = items;
    activeSuggestionIndex = -1;
    if (items.length === 0) { hideSuggestions(); return; }
    suggestionsDiv.innerHTML = "";
    items.forEach(function (skill, index) {
      var item = document.createElement("div");
      item.className = "suggestion-item";
      item.textContent = skill;
      item.setAttribute("role", "option");
      item.setAttribute("id", "skills-suggestion-" + index);
      item.setAttribute("aria-selected", "false");
      // Prevent the input blur handler from closing the menu before click runs
      item.addEventListener("mousedown", function (evt) { evt.preventDefault(); });
      item.addEventListener("mouseenter", function () { activeSuggestionIndex = index; renderActiveSuggestion(); });
      item.addEventListener("click", function () { selectSuggestion(skill); });
      suggestionsDiv.appendChild(item);
    });
    suggestionsDiv.style.display = "block";
    skillsTextInput.setAttribute("aria-expanded", "true");
  }

  function updateQuickPickState() {
    quickPickChips.forEach(function (chip) {
      var isActive = isSkillSelected(chip.getAttribute("data-skill") || "");
      chip.classList.toggle("active", isActive);
      chip.setAttribute("aria-pressed", isActive ? "true" : "false");
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

  // Add/toggle skill on quick-pick chip click
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");
      if (!skill) return;
      if (isSkillSelected(skill)) { removeSkill(skill); } else { addSkill(skill); }
      skillsTextInput.value = "";
      hideSuggestions();
    });
  });

  // Show suggestions on input
  skillsTextInput.addEventListener("input", function (evt) {
    var typedValue = evt.target.value.trim();
    if (typedValue.length === 0) { hideSuggestions(); return; }
    displaySuggestions(getFilteredSkills(typedValue));
  });

  skillsTextInput.addEventListener("focus", function () {
    if (skillsTextInput.value.trim()) displaySuggestions(getFilteredSkills(skillsTextInput.value));
  });

  // Hide suggestions when input loses focus
  skillsTextInput.addEventListener("blur", function () {
    setTimeout(function () { hideSuggestions(); }, 150);
  });

  if (skillWrap) {
    skillWrap.addEventListener("click", function () { skillsTextInput.focus(); });
  }

  document.addEventListener("click", function (evt) {
    if (skillWrap && !skillWrap.contains(evt.target)) hideSuggestions();
  });

  function removeSkill(skill) {
    // Rebuild the array without the skill that was just removed
    selectedSkills = selectedSkills.filter(function (s) { return normalizeSkill(s) !== normalizeSkill(skill); });
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
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
    if (!skillsHidden) return;
    // Keep the hidden <input> in sync for form serialisation
    // The API expects a comma-separated string, so join the array that way
    skillsHidden.value = selectedSkills.join(", ");
  }

  updateQuickPickState();

  function hideSuggestions() {
    visibleSuggestions = [];
    activeSuggestionIndex = -1;
    if (suggestionsDiv) {
      suggestionsDiv.style.display = "none";
      suggestionsDiv.classList.remove("show");
      suggestionsDiv.innerHTML = "";
    }
    syncSuggestionsA11yState();
    suggestions.style.display = "none";
    suggestions.textContent = "";
    skillsInput.setAttribute("aria-expanded", "false");
  }

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
      
      // Check if skill is already selected for multi-select styling
      var isSelected = isSkillSelected(skill);
      if (isSelected) {
        item.classList.add("selected");
      }
      
      item.textContent = skill;
      item.setAttribute("role", "option");
      item.setAttribute("id", "skills-suggestion-" + index);
      item.setAttribute("aria-selected", isSelected ? "true" : "false");

      // Prevent the input blur handler from closing the menu before click runs.
      item.addEventListener("mousedown", function (evt) {
        evt.preventDefault();
      });

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
        selectSuggestion(skill);
        // Keep dropdown open if clicking from dropdown (multi-select mode)
        if (suggestionsDiv.classList.contains("show")) {
          displaySuggestions(items);
          skillsTextInput.focus();
        }
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
    if (!document.getElementById("level").value) {
      showFieldError("level-error", "Please select your experience level.");
      valid = false;
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
    if (!document.getElementById("time").value) {
      showFieldError("time-error", "Please select your time availability.");
      valid = false;
    }

    return valid;
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

  // Manages the loading state of the form and results section(whats visible or not)
  function setLoadingState(isLoading) {
    // Disable the button so the user can't accidentally submit twice
    submitBtn.disabled = isLoading;
    submitBtn.setAttribute("aria-busy", isLoading);
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline-flex" : "none";

    if (isLoading) {
      resultsGrid.innerHTML = "";         
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "none";
      resultsEmptyEl.textContent = "";
      resultsLoadingEl.style.display = "block";
      resultsSection.style.display = "block";
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } else {
      resultsLoadingEl.style.display  = "none";
      resultsGrid.style.display       = "grid"; //switch back to gird layout 
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

  //takes the array of projects from the api and draws them on the page as cards
  //if array is empty it shows the "no results" message instead
  function renderResults(projects, message) {
    console.log("Rendering results with projects:", projects);
    console.log("Message:", message);
    
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    // Clear out any cards from a previous search before showing new ones
    resultsGrid.innerHTML = "";
    recordSearch();

    if (!projects || projects.length === 0) {
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";

      // Show a friendly custom message when the user selected an interest
      var selectedInterest = document.getElementById("interest")?.value;
      if (selectedInterest) {
        emptyMessageEl.textContent = "No projects are currently available for this interest. Please check back later or try a different area.";
      } else if (message) {
        emptyMessageEl.textContent = message;
      } else {
        emptyMessageEl.textContent = "Try adjusting your skills or choosing a different interest area.";
      }

  // Clear out previous results before rendering new ones
  resultsGrid.innerHTML = "";

  // If no projects are returned, show the empty state message
  if (!projects || projects.length === 0) {
    resultsGrid.style.display = "none";
    resultsEmptyEl.style.display = "block";

    projects.forEach(function (project) {
      resultsGrid.appendChild(buildProjectCard(project));
    });

    recordSearch();
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  function buildProjectCard(project) {
    
    var card = document.createElement("div");
    card.className = "project-card";

    // Console logging for debugging
    console.log("Building card for project:", project);
    console.log("Project ID:", project.id);

    // Title
    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;

    // Description (truncated for visual consistency)
    var desc = document.createElement("p");
    desc.className = "project-card-desc";
    // Cut description to 120 chars so all cards stay the same height
    desc.textContent = truncate(project.description, 120);

    // Tags row
    var tagsRow = document.createElement("div");
    tagsRow.className = "project-card-tags";

    // Show all project skills as tags so users can see the full match
    (project.skills || []).forEach(function (skill) {
      tagsRow.appendChild(createTag(skill, "skill"));
    });

    // Level tag (colour-coded via CSS class)
    // Lowercase so it matches the CSS class names like "level beginner", "level advanced"
    tagsRow.appendChild(createTag(project.level, "level " + (project.level || "").toLowerCase()));

    // Time tag
    tagsRow.appendChild(createTag("Time: " + project.time, "time"));

    // Footer with view-details link
    var footer = document.createElement("div");
    footer.className = "project-card-footer";

    var link = document.createElement("a");
    link.className = "btn-details";
    link.textContent = "View Full Project";
    link.href = "/project/" + project.id; //each project has a unique id
    
    console.log("Created link with href:", link.href);

    link.href = "/project/" + project.id;
    footer.appendChild(saveButton);
    footer.appendChild(link);

    // Assemble the card in order
    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tagsRow);
    card.appendChild(footer);
    return card;
  }

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

    return card;
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

  function truncate(text, maxLength) {
    // Safety check — just return empty string if text is missing
    if (!text) return "";
    // Only add "..." if the text is actually longer than the limit
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

} // end isIndexPage


// ============================================================
// DETAIL PAGE
// ============================================================
if (isDetailPage) {

  var codePanel         = document.getElementById("code-panel"); // sliding panel that shows the starter code "
  var codePanelOverlay  = document.getElementById("code-panel-overlay"); // background overlay 
  var codeContentEl     = document.getElementById("code-content"); // <pre> element inside the panel where the code will be inserted
  var codePanelFilename = document.getElementById("code-panel-filename"); // filename display
  var btnViewCode       = document.getElementById("btn-view-code"); // button to open the code panel on desktop
  var btnViewCodeSm     = document.getElementById("btn-view-code-sm"); // button to open the code panel on mobile (could be the same button with different styling, but we have two here for simplicity)
  var btnClosePanel     = document.getElementById("code-panel-close"); // button inside the panel to close it

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
  var btnCopyCode  = document.getElementById("btn-copy-code");
  var copyToast    = document.getElementById("copy-toast"); //popup msg when copied 
  var toastTimeout = null; 

  //shows the "copied to clipboard" state on the button and the toast message, then resets after a short delay
  function showCopySuccess() {
    if (!btnCopyCode) return;

    // Swap icons on the button(copy and checkmark icons)
    var copyIcon  = btnCopyCode.querySelector(".copy-icon");
    var checkIcon = btnCopyCode.querySelector(".check-icon");
    var btnLabel  = btnCopyCode.querySelector(".copy-btn-label");
    if (copyIcon)  copyIcon.style.display  = "none";
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
  } // end github modal handlers

    /* ---- Scroll-to-top button ---- */
      
  var SCROLL_THRESHOLD = 300;
  var scrollTopBtn = document.getElementById('scroll-top-btn');

  function handleScroll() {
    if (!scrollTopBtn) return;
    if (window.pageYOffset > SCROLL_THRESHOLD) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
  }

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  if (scrollTopBtn) {
    window.addEventListener('scroll', handleScroll);
    scrollTopBtn.addEventListener('click', scrollToTop);
  }
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

if (
    openModalBtn &&
    closeModalBtn &&
    modal &&
    githubInput &&
    fetchBtn &&
    errorMsg
) {
// 1. Open Github Input Modal
  openModalBtn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
      githubInput.focus();
  });

  // 2. Close Github Input Modal
  const closeGithubModal = () => {
      modal.classList.remove('active');
      githubInput.value = '';
      errorMsg.textContent = '';
  };

  closeModalBtn.addEventListener('click', closeGithubModal);

  // Close on clicking outside the card
  modal.addEventListener('click', (e) => {
      if (e.target === modal) closeGithubModal();
  });

  // 3. Fetch Skills Logic
  fetchBtn.addEventListener('click', async () => {
      const username = githubInput.value.trim();
      if (!username) return;

      fetchBtn.disabled = true;
      fetchBtn.textContent = 'Syncing...';

      try {
          const response = await fetch(`https://api.github.com/users/${username}/repos`);
          if (!response.ok) throw new Error();
          
          const repos = await response.json();
          const langs = [...new Set(repos.map(r => r.language).filter(Boolean))];

          if (langs.length > 0) {
              langs.forEach(lang => {
                  if (typeof addSkill === 'function') addSkill(lang);
              });
              closeGithubModal();
          } else {
              errorMsg.textContent = "No public languages found.";
          }
      } catch (err) {
          errorMsg.textContent = err.message ?? "Failed to fetch skills";
      } finally {
          fetchBtn.disabled = false;
          fetchBtn.textContent = 'Fetch Skills';
      }
  });
  update();
})();

(function initScrollSpy() {
  var sections = document.querySelectorAll("section[id], header[id]");
  var navLinks = document.querySelectorAll(".nav-link, .nav-mobile-link");

  if (sections.length === 0 || navLinks.length === 0) return;

  var observerOptions = {
    root: null,
    rootMargin: "-20% 0px -70% 0px",
    threshold: 0
  };

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
}());

  sections.forEach(function (sec) {
    observer.observe(sec);
  });
})();
