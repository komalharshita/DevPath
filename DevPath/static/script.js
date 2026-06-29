// script.js — DevPath client-side logic
//
// Responsibilities:
//   - Mobile navigation toggle
//   - Skill chip manager (add/remove skills)
//   - Form validation with per-field error messages
//   - Recommendation API call and loading states
//   - Result card rendering
//   - Code viewer panel (detail page)
//   - Filter State Persistence Layer (LocalStorage Hydration)

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
      <button class="theme-preview-card" data-theme-target="light" style="background:transparent; border:2px solid var(--border); border-radius:var(--r-md); padding:1rem; cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:1rem; transition:all 0.2s ease;">
        <div class="preview-mockup" style="width:100%; background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:8px; display:flex; flex-direction:column; gap:6px;">
          <div style="width:100%; height:12px; background:#f1f5f9; border-radius:3px;"></div>
          <div style="width:100%; height:6px; background:#cbd5e1; border-radius:2px;"></div>
          <div style="width:60%; height:6px; background:#cbd5e1; border-radius:2px;"></div>
          <div style="width:100%; margin-top:4px; padding:4px 0; background:#3b82f6; border-radius:3px; color:#fff; font-size:8px; text-align:center; font-weight:bold;">Button</div>
        </div>
        <span class="preview-label" style="font-weight:600; color:var(--text-heading);">Light Theme</span>
      </button>
      
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
    
    var isDark = theme === "dark";
    document.querySelectorAll(".theme-toggle").forEach(function(btn) {
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    });

    cards.forEach(function(card) {
      if (card.getAttribute("data-theme-target") === theme) {
        card.style.borderColor = "var(--accent)";
      } else {
        card.style.borderColor = "var(--border)";
      }
    });
  }

  var activeTheme = html.getAttribute("data-theme") || localStorage.getItem("theme") || "light";
  syncTheme(activeTheme);

  document.querySelectorAll(".theme-toggle").forEach(function(btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    });
  });

  function closeModal() {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
  }

  closeBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", function(e) {
    if (e.target === modal) closeModal();
  });

  cards.forEach(function(card) {
    card.addEventListener("click", function() {
      var theme = this.getAttribute("data-theme-target");
      syncTheme(theme);
      setTimeout(closeModal, 150);
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
var isIndexPage = !!document.getElementById("recommend-form");
var isDetailPage = typeof PROJECT_ID !== "undefined";

// ============================================================
// Mobile navigation toggle (runs on all pages)
// ============================================================
(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu   = document.getElementById("nav-mobile-menu");

  if (!toggle || !menu) return;

  toggle.addEventListener("click", function () {
    var isOpen = menu.classList.toggle("open");
    toggle.classList.toggle("open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen);
  });

  menu.querySelectorAll(".nav-mobile-link").forEach(function (link) { 
    link.addEventListener("click", function () { 
      menu.classList.remove("open"); 
      toggle.classList.remove("open");
    });
  });
})();

// ============================================================
// INDEX PAGE (QUESTIONNAIRE & FILTERS STATE CONFIG)
// ============================================================
if (isIndexPage) {
  var form              = document.getElementById("recommend-form");
  var skillsHidden      = document.getElementById("skills");
  var skillsTextInput   = document.getElementById("skills-input");
  var chipsSelectedEl   = document.getElementById("skill-chips-selected");
  var quickPickChips    = document.querySelectorAll(".skill-chip");
  var suggestionsDiv    = document.getElementById("skills-suggestions");
  var skillWrap         = document.getElementById("skill-input-wrap");
  var clearFiltersBtn   = document.getElementById("clear-filters-btn");

  var selectedSkills = [];
  var STORAGE_KEY = "devpath_onboarding_filters";

  // ----------------------------------------------------------
  // LocalStorage State Sync Engines
  // ----------------------------------------------------------
  function saveFormStateToStorage() {
    var filterPayload = {
      skills: selectedSkills,
      level: document.getElementById("level") ? document.getElementById("level").value : "",
      interest: document.getElementById("interest") ? document.getElementById("interest").value : "",
      time: document.getElementById("time") ? document.getElementById("time").value : ""
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filterPayload));
    } catch (e) {
      console.warn("Failed saving form persistence layer states:", e);
    }
  }

  function hydrateFormStateFromStorage() {
    try {
      var cachedData = localStorage.getItem(STORAGE_KEY);
      if (!cachedData) return;
      
      var parsed = JSON.parse(cachedData);
      
      // Hydrate skill list chips
      if (parsed.skills && Array.isArray(parsed.skills)) {
        selectedSkills = parsed.skills;
        renderSelectedChips();
        syncSkillsHiddenInput();
        updateQuickPickState();
      }
      
      // Hydrate standard drop-down selection options
      if (parsed.level && document.getElementById("level")) {
        document.getElementById("level").value = parsed.level;
      }
      if (parsed.interest && document.getElementById("interest")) {
        document.getElementById("interest").value = parsed.interest;
      }
      if (parsed.time && document.getElementById("time")) {
        document.getElementById("time").value = parsed.time;
      }
    } catch (e) {
      console.error("Error loading questionnaire form hydration cache:", e);
    }
  }

  function purgeFormStorage() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {}
  }

  // Bind change listeners to select dropdown fields for instant persistence
  ["level", "interest", "time"].forEach(function(fieldId) {
    var element = document.getElementById(fieldId);
    if (element) {
      element.addEventListener("change", saveFormStateToStorage);
    }
  });

  // ----------------------------------------------------------
  // Skill chip managers
  // ----------------------------------------------------------
  var availableSkills = [];
  if (typeof skills !== "undefined" && Array.isArray(skills)) {
    availableSkills = skills.map(function (item) { return item.label; }).filter(Boolean);
  } else {
    quickPickChips.forEach(function (chip) {
      var s = chip.getAttribute("data-skill");
      if (s) availableSkills.push(s);
    });
  }

  function normalizeSkill(skill) { return skill.trim().toLowerCase(); }

  function isSkillSelected(skill) {
    return selectedSkills.some(function (s) {
      return normalizeSkill(s) === normalizeSkill(skill);
    });
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

  function addSkill(rawSkill) {
    var skill = getCanonicalSkill(rawSkill);
    if (!skill || isSkillSelected(skill)) return;

    selectedSkills.push(skill);
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    clearFieldError("skills-error");
    saveFormStateToStorage();

    if (skillsTextInput) skillsTextInput.focus();
  }

  function removeSkill(skill) {
    selectedSkills = selectedSkills.filter(function (selectedSkill) {
      return normalizeSkill(selectedSkill) !== normalizeSkill(skill);
    });
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    saveFormStateToStorage();
  }

  function renderSelectedChips() {
    chipsSelectedEl.innerHTML = "";
    selectedSkills.forEach(function (skill) {
      var chipEl = document.createElement("span");
      chipEl.className = "skill-chip-selected";
      chipEl.textContent = skill;

      var removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "skill-chip-remove";
      removeBtn.innerHTML = "&times;";
      removeBtn.setAttribute("aria-label", "Remove " + skill);
      removeBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        removeSkill(skill);
      });

      chipEl.appendChild(removeBtn);
      chipsSelectedEl.appendChild(chipEl);
    });
  }

  function syncSkillsHiddenInput() {
    if (!skillsHidden) return;
    skillsHidden.value = selectedSkills.join(", ");
  }

  function updateQuickPickState() {
    quickPickChips.forEach(function (chip) {
      var isActive = isSkillSelected(chip.getAttribute("data-skill") || "");
      chip.classList.toggle("active", isActive);
      chip.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }

  // ----------------------------------------------------------
  // Suggestion Dropdown UI Layer
  // ----------------------------------------------------------
  var activeSuggestionIndex = -1;
  var visibleSuggestions = [];

  function displaySuggestions(items) {
    if (!suggestionsDiv) return;
    visibleSuggestions = items;
    activeSuggestionIndex = -1;
    if (items.length === 0) { hideSuggestions(); return; }
    
    suggestionsDiv.innerHTML = "";
    items.forEach(function (skill, index) {
      var item = document.createElement("div");
      item.className = "suggestion-item";
      if (isSkillSelected(skill)) item.classList.add("selected");
      item.textContent = skill;
      item.setAttribute("role", "option");
      item.setAttribute("id", "skills-suggestion-" + index);
      item.setAttribute("aria-selected", "false");

      item.addEventListener("mousedown", function (evt) { evt.preventDefault(); });
      item.addEventListener("mouseenter", function () { 
        activeSuggestionIndex = index; 
        renderActiveSuggestion(); 
      });
      item.addEventListener("click", function () {
        addSkill(skill);
        skillsTextInput.value = "";
        hideSuggestions();
      });
      suggestionsDiv.appendChild(item);
    });
    suggestionsDiv.style.display = "block";
    skillsTextInput.setAttribute("aria-expanded", "true");
  }

  function hideSuggestions() {
    visibleSuggestions = [];
    activeSuggestionIndex = -1;
    if (suggestionsDiv) {
      suggestionsDiv.style.display = "none";
      suggestionsDiv.innerHTML = "";
    }
    if (skillsTextInput) skillsTextInput.setAttribute("aria-expanded", "false");
  }

  function renderActiveSuggestion() {
    if (!suggestionsDiv) return;
    suggestionsDiv.querySelectorAll(".suggestion-item").forEach(function (item, index) {
      var isActive = index === activeSuggestionIndex;
      item.classList.toggle("suggestion-item--active", isActive);
      item.setAttribute("aria-selected", isActive ? "true" : "false");
    });
  }

  // Input event hooks for query lookups
  if (skillsTextInput) {
    skillsTextInput.addEventListener("input", function (evt) {
      var typedValue = evt.target.value.trim();
      if (typedValue.length === 0) { hideSuggestions(); return; }
      displaySuggestions(getFilteredSkills(typedValue));
    });

    skillsTextInput.addEventListener("focus", function () {
      if (skillsTextInput.value.trim()) displaySuggestions(getFilteredSkills(skillsTextInput.value));
    });

    skillsTextInput.addEventListener("blur", function () {
      setTimeout(function () { hideSuggestions(); }, 150);
    });

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
          addSkill(visibleSuggestions[activeSuggestionIndex]);
          skillsTextInput.value = "";
          hideSuggestions();
          return;
        }
        if (skillsTextInput.value.trim()) {
          addSkill(skillsTextInput.value);
          skillsTextInput.value = "";
        }
        hideSuggestions();
      }
    });
  }

  // Hook Quick Pick chips
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");
      if (!skill) return;
      if (isSkillSelected(skill)) { removeSkill(skill); } else { addSkill(skill); }
      if (skillsTextInput) skillsTextInput.value = "";
      hideSuggestions();
    });
  });

  if (skillWrap) {
    skillWrap.addEventListener("click", function () { if (skillsTextInput) skillsTextInput.focus(); });
  }

  document.addEventListener("click", function (evt) {
    if (skillWrap && !skillWrap.contains(evt.target)) hideSuggestions();
  });

  // ----------------------------------------------------------
  // Form resets and clear buttons
  // ----------------------------------------------------------
  function clearAllFormSelections() {
    selectedSkills = [];
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    ["skills-error", "level-error", "interest-error", "time-error"].forEach(clearFieldError);
    purgeFormStorage();
  }

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function () {
      if (form) {
        form.reset();
        clearAllFormSelections();
        if (skillsTextInput) skillsTextInput.focus();
      }
    });
  }

  if (form) {
    form.addEventListener("reset", function () {
      window.setTimeout(function () {
        clearAllFormSelections();
        if (skillsTextInput) skillsTextInput.focus();
      }, 0);
    });

    // Clear saved states upon successful form data submission
    form.addEventListener("submit", function (e) {
      if (validateForm()) {
        purgeFormStorage();
      } else {
        e.preventDefault();
      }
    });
  }

  // ----------------------------------------------------------
  // Form Validation Engine
  // ----------------------------------------------------------
  function showFieldError(fieldId, message) {
    var el = document.getElementById(fieldId);
    if (el) el.textContent = message;
  }

  function clearFieldError(fieldId) {
    var el = document.getElementById(fieldId);
    if (el) el.textContent = "";
  }

  function validateForm() {
    var valid = true;
    if (selectedSkills.length === 0 && (!skillsHidden || !skillsHidden.value.trim())) {
      showFieldError("skills-error", "Please add at least one skill.");
      valid = false;
    } else {
      clearFieldError("skills-error");
    }
    if (document.getElementById("level") && !document.getElementById("level").value) {
      showFieldError("level-error", "Please select your experience level.");
      valid = false;
    } else {
      clearFieldError("level-error");
    }
    if (document.getElementById("interest") && !document.getElementById("interest").value) {
      showFieldError("interest-error", "Please select an area of interest.");
      valid = false;
    } else {
      clearFieldError("interest-error");
    }
    if (document.getElementById("time") && !document.getElementById("time").value) {
      showFieldError("time-error", "Please select your time availability.");
      valid = false;
    } else {
      clearFieldError("time-error");
    }
    return valid;
  }

  // Initialize and trigger data hydration cache load
  hydrateFormStateFromStorage();
}
