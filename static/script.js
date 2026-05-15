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
// Detect which page we are on
// ============================================================
var isIndexPage  = !!document.getElementById("recommend-form");
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
  var form              = document.getElementById("recommend-form");
  var submitBtn         = document.getElementById("submit-btn");
  var btnLabel          = document.getElementById("btn-label");
  var btnLoading        = document.getElementById("btn-loading");
  var resultsSection    = document.getElementById("results-section");
  var resultsGrid       = document.getElementById("results-grid");
  var resultsLoadingEl  = document.getElementById("results-loading");
  var resultsEmptyEl    = document.getElementById("results-empty");
  var emptyMessageEl    = document.getElementById("empty-message");
  var skillsHidden      = document.getElementById("skills");
  var skillsTextInput   = document.getElementById("skills-input");
  var chipsSelectedEl   = document.getElementById("skill-chips-selected");
  var quickPickChips    = document.querySelectorAll(".skill-chip");

  // Tracks currently selected skills to prevent duplicates
  var selectedSkills = [];


  // ----------------------------------------------------------
  // Skill chip manager
  // ----------------------------------------------------------

  // Add skill on Enter key in the text input
  skillsTextInput.addEventListener("keydown", function (evt) {
    if (evt.key === "Enter") {
      evt.preventDefault();
      var value = skillsTextInput.value.trim();
      if (value) {
        addSkill(value);
        skillsTextInput.value = "";
      }
    }
  });

  // Add skill on quick-pick chip click
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      addSkill(chip.getAttribute("data-skill"));
      chip.classList.add("active");
    });
  });

  // Focus the text input when clicking anywhere in the chip wrap
  var skillWrap = document.getElementById("skill-input-wrap");
  if (skillWrap) {
    skillWrap.addEventListener("click", function () { skillsTextInput.focus(); });
  }

  function addSkill(rawSkill) {
    var skill = rawSkill.trim();
    if (!skill) return;

    // Block duplicate entries (case-insensitive)
    var isDuplicate = selectedSkills.some(function (s) {
      return s.toLowerCase() === skill.toLowerCase();
    });
    if (isDuplicate) return;

    selectedSkills.push(skill);
    renderSelectedChips();
    syncSkillsHiddenInput();
    clearFieldError("skills-error");
  }

  function removeSkill(skill) {
    selectedSkills = selectedSkills.filter(function (s) { return s !== skill; });
    renderSelectedChips();
    syncSkillsHiddenInput();

    // Un-highlight the quick-pick button if it matches the removed skill
    quickPickChips.forEach(function (chip) {
      if (chip.getAttribute("data-skill") === skill) {
        chip.classList.remove("active");
      }
    });
  }

  function renderSelectedChips() {
    chipsSelectedEl.innerHTML = "";
    selectedSkills.forEach(function (skill) {
      var chipEl = document.createElement("span");
      chipEl.className = "skill-chip-selected";
      chipEl.textContent = skill;

      // Remove button for each chip
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
    // Keep the hidden <input> in sync for form serialisation
    skillsHidden.value = selectedSkills.join(", ");
  }


  // ----------------------------------------------------------
  // Form validation
  // ----------------------------------------------------------

  function showFieldError(fieldId, message) {
    var el = document.getElementById(fieldId);
    if (el) el.textContent = message;
  }

  function clearFieldError(fieldId) {
    var el = document.getElementById(fieldId);
    if (el) el.textContent = "";
  }

  function clearAllErrors() {
    ["skills-error", "level-error", "interest-error", "time-error"].forEach(clearFieldError);
    var generalErr = document.getElementById("form-error-general");
    if (generalErr) generalErr.textContent = "";
  }

  function validateForm() {
    var valid = true;

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

    if (!validateForm()) return;

    setLoadingState(true);

    var payload = {
      skills:   skillsHidden.value.trim() || skillsTextInput.value.trim(),
      level:    document.getElementById("level").value,
      interest: document.getElementById("interest").value,
      time:     document.getElementById("time").value
    };

    fetch("/api/recommend", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    })
      .then(function (res) { return res.json(); })
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
        setLoadingState(false);
        var generalErr = document.getElementById("form-error-general");
        if (generalErr) generalErr.textContent = "Something went wrong. Please try again.";
        console.error("API request failed:", err);
      });
  });

  function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    btnLabel.style.display   = isLoading ? "none"   : "inline";
    btnLoading.style.display = isLoading ? "inline" : "none";

    if (isLoading) {
      // Show the results section with only the loading indicator visible
      resultsSection.style.display    = "block";
      resultsLoadingEl.style.display  = "block";
      resultsGrid.style.display       = "none";
      resultsEmptyEl.style.display    = "none";
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } else {
      resultsLoadingEl.style.display  = "none";
      resultsGrid.style.display       = "grid";
    }
  }


  // ----------------------------------------------------------
  // Render result cards
  // ----------------------------------------------------------

  function renderResults(projects, message) {
    resultsSection.style.display    = "block";
    resultsLoadingEl.style.display  = "none";
    resultsGrid.innerHTML           = "";
    
    // Store current projects for reference
    currentProjects = projects || [];

    if (!projects || projects.length === 0) {
      resultsGrid.style.display      = "none";
      resultsEmptyEl.style.display   = "block";
      showSearchInput(false); // Hide search when no results
      if (message && emptyMessageEl) emptyMessageEl.textContent = message;
      resultsSection.scrollIntoView({ behavior: "smooth" });
      return;
    }

    resultsEmptyEl.style.display  = "none";
    resultsGrid.style.display     = "grid";

    projects.forEach(function (project) {
      resultsGrid.appendChild(buildProjectCard(project));
    });

    // Show search input and setup filter (only once)
    showSearchInput(true);
    if (!searchInput) setupFilter();

    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  function buildProjectCard(project) {
    var card = document.createElement("div");
    card.className = "project-card";

    // Title
    var title = document.createElement("h3");
    title.className   = "project-card-title";
    title.textContent = project.title;

    // Description (truncated for visual consistency)
    var desc = document.createElement("p");
    desc.className   = "project-card-desc";
    desc.textContent = truncate(project.description, 120);

    // Tags row
    var tagsRow = document.createElement("div");
    tagsRow.className = "project-card-tags";

    // Show the first two skills as tags
    (project.skills || []).slice(0, 2).forEach(function (skill) {
      tagsRow.appendChild(createTag(skill, "skill"));
    });

    // Level tag (colour-coded via CSS class)
    var levelClass = "level " + (project.level || "").toLowerCase();
    tagsRow.appendChild(createTag(project.level, levelClass));

    // Time tag
    tagsRow.appendChild(createTag("Time: " + project.time, "time"));

    // Footer with view-details link
    var footer = document.createElement("div");
    footer.className = "project-card-footer";

    var link = document.createElement("a");
    link.className   = "btn-details";
    link.textContent = "View Full Project";
    link.href        = "/project/" + project.id;

    footer.appendChild(link);

    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tagsRow);
    card.appendChild(footer);

    return card;
  }

  function createTag(text, type) {
    var span = document.createElement("span");
    span.className   = "project-tag project-tag--" + type;
    span.textContent = text;
    return span;
  }

  function truncate(text, maxLength) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

  // ----------------------------------------------------------
  // Filter projects based on search input
  // ----------------------------------------------------------
  var searchInput = null;
  var currentProjects = [];

  function setupFilter() {
    searchInput = document.getElementById("results-search");
    if (!searchInput) return;
    
    searchInput.addEventListener("input", function (e) {
      var searchTerm = e.target.value.trim().toLowerCase();
      var cards = resultsGrid.querySelectorAll(".project-card");
      
      cards.forEach(function (card) {
        var title = card.querySelector(".project-card-title")?.textContent.toLowerCase() || "";
        var desc = card.querySelector(".project-card-desc")?.textContent.toLowerCase() || "";
        
        if (searchTerm === "" || title.includes(searchTerm) || desc.includes(searchTerm)) {
          card.style.display = "";
        } else {
          card.style.display = "none";
        }
      });
    });
  }

  function showSearchInput(show) {
    var wrap = document.getElementById("results-search-wrap");
    if (wrap) {
      wrap.style.display = show ? "block" : "none";
      if (show && searchInput) searchInput.value = "";
    }
  }

} // end isIndexPage


// ============================================================
// DETAIL PAGE
// ============================================================
if (isDetailPage) {

  var codePanel         = document.getElementById("code-panel");
  var codePanelOverlay  = document.getElementById("code-panel-overlay");
  var codeContentEl     = document.getElementById("code-content");
  var codePanelFilename = document.getElementById("code-panel-filename");
  var btnViewCode       = document.getElementById("btn-view-code");
  var btnViewCodeSm     = document.getElementById("btn-view-code-sm");
  var btnClosePanel     = document.getElementById("code-panel-close");

  // Cache flag so code is only fetched once per page load
  var codeFetched = false;

  function openCodePanel() {
    if (!codePanel) return;
    codePanel.classList.add("active");
    if (codePanelOverlay) codePanelOverlay.classList.add("active");
    document.body.style.overflow = "hidden";

    if (!codeFetched) fetchStarterCode();
  }

  function closeCodePanel() {
    if (!codePanel) return;
    codePanel.classList.remove("active");
    if (codePanelOverlay) codePanelOverlay.classList.remove("active");
    document.body.style.overflow = "";
  }

  function fetchStarterCode() {
    if (codeContentEl) codeContentEl.textContent = "Loading starter code...";

    fetch("/project/" + PROJECT_ID + "/code")
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.error) {
          if (codeContentEl) codeContentEl.textContent = "Error: " + data.error;
          return;
        }
        if (codePanelFilename) codePanelFilename.textContent = data.filename;
        if (codeContentEl)     codeContentEl.textContent     = data.code;
        codeFetched = true;
      })
      .catch(function () {
        if (codeContentEl) {
          codeContentEl.textContent = "Could not load starter code. Try downloading it instead.";
        }
      });
  }

  // Attach open/close handlers
  if (btnViewCode)   btnViewCode.addEventListener("click", openCodePanel);
  if (btnViewCodeSm) btnViewCodeSm.addEventListener("click", openCodePanel);
  if (btnClosePanel) btnClosePanel.addEventListener("click", closeCodePanel);

  if (codePanelOverlay) {
    codePanelOverlay.addEventListener("click", closeCodePanel);
  }

  document.addEventListener("keydown", function (evt) {
    if (evt.key === "Escape") closeCodePanel();
  });

  // ----------------------------------------------------------
  // Copy Code button
  // ----------------------------------------------------------
  var btnCopyCode  = document.getElementById("btn-copy-code");
  var copyToast    = document.getElementById("copy-toast");
  var toastTimeout = null;

  function showCopySuccess() {
    if (!btnCopyCode) return;

    // Swap icons on the button
    var copyIcon  = btnCopyCode.querySelector(".copy-icon");
    var checkIcon = btnCopyCode.querySelector(".check-icon");
    var btnLabel  = btnCopyCode.querySelector(".copy-btn-label");

    if (copyIcon)  copyIcon.style.display  = "none";
    if (checkIcon) checkIcon.style.display = "inline";
    if (btnLabel)  btnLabel.textContent    = "Copied!";
    btnCopyCode.classList.add("copied");
    btnCopyCode.disabled = true;

    // Show toast
    if (copyToast) {
      copyToast.classList.add("show");
    }

    // Auto-reset after 2.5 s
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(function () {
      if (copyIcon)  copyIcon.style.display  = "inline";
      if (checkIcon) checkIcon.style.display = "none";
      if (btnLabel)  btnLabel.textContent    = "Copy Code";
      btnCopyCode.classList.remove("copied");
      btnCopyCode.disabled = false;
      if (copyToast) copyToast.classList.remove("show");
    }, 2500);
  }

  if (btnCopyCode) {
    btnCopyCode.addEventListener("click", function () {
      var code = codeContentEl ? codeContentEl.textContent : "";
      if (!code || code === "Loading..." || code === "Loading starter code...") return;

      // Use Clipboard API with textarea fallback
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(showCopySuccess).catch(function () {
          fallbackCopy(code);
        });
      } else {
        fallbackCopy(code);
      }
    });
  }

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.cssText = "position:fixed;top:-9999px;left:-9999px;opacity:0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try { document.execCommand("copy"); showCopySuccess(); } catch (e) { /* silent fail */ }
    document.body.removeChild(ta);
  }

} // end isDetailPage