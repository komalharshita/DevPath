// script.js — DevPath client-side logic
//
// Responsibilities:
//   - Mobile navigation toggle
//   - Skill chip manager (add/remove skills)
//   - Form validation with per-field error messages
//   - Recommendation API call and loading states
//   - Result card rendering
//   - Code viewer panel (detail page)
//   - Interactive roadmap progress tracking & persistence (Fully Configured)

// ============================================================
// Detect which page we are on
// ============================================================
// !! trick turns the DOM result into a simple true/false
var isIndexPage  = !!document.getElementById("recommend-form");
// PROJECT_ID is set by the server only on detail pages, so if it's missing we're elsewhere
var isDetailPage = typeof PROJECT_ID !== "undefined";


// ============================================================
// Mobile navigation toggle (runs on all pages)
// ============================================================
(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu = document.getElementById("nav-mobile-menu");

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
  var form = document.getElementById("recommend-form");
  var submitBtn = document.getElementById("submit-btn");
  var btnLabel = document.getElementById("btn-label");
  var btnLoading = document.getElementById("btn-loading");
  var resultsSection = document.getElementById("results-section");
  var resultsGrid = document.getElementById("results-grid");
  var resultsLoadingEl = document.getElementById("results-loading");
  var resultsEmptyEl = document.getElementById("results-empty");
  var emptyMessageEl = document.getElementById("empty-message");
  var skillsHidden = document.getElementById("skills");
  
  // Safely grab the active text field among duplicate template input elements
  var skillsTextInput = document.getElementById("skills-input");
  if (skillsTextInput && skillsTextInput.tagName !== "INPUT") {
      skillsTextInput = document.querySelector(".skill-input-wrap input[type='text']");
  }
  
  var chipsSelectedEl = document.getElementById("skill-chips-selected");
  var quickPickChips = document.querySelectorAll(".skill-chip");

  // Tracks currently selected skills to prevent duplicates
  var selectedSkills = [];


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

  availableSkills = availableSkills.filter(function (skill, index, list) {
    return typeof skill === "string" && skill.trim() &&
      list.findIndex(function (item) {
        return item.toLowerCase() === skill.toLowerCase();
      }) === index;
  });

  if (suggestionsDiv) {
    suggestionsDiv.setAttribute("role", "listbox");
  }

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
    if (skillsTextInput) {
      skillsTextInput.setAttribute("aria-expanded", visibleSuggestions.length > 0 ? "true" : "false");
    }
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
    if (skillsTextInput) {
      skillsTextInput.value = "";
      hideSuggestions();
      skillsTextInput.focus();
    }
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

      // Prevent input blur handler from closing menu before click runs
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

  // Bind keyboard interactions safely if text node exists
  if (skillsTextInput) {
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

    skillsTextInput.addEventListener("blur", function () {
      setTimeout(function () { hideSuggestions(); }, 150);
    });
  }

  if (skillWrap && skillsTextInput) {
    skillWrap.addEventListener("click", function () {
      skillsTextInput.focus();
    });
  }

  // Add skill on quick-pick chip click
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      addSkill(chip.getAttribute("data-skill"));
      hideSuggestions();
      if (skillsTextInput) skillsTextInput.value = "";
    });
  });

  document.addEventListener("click", function (evt) {
    if (skillWrap && !skillWrap.contains(evt.target)) {
      hideSuggestions();
    }
  });

  function addSkill(rawSkill) {
    var skill = getCanonicalSkill(rawSkill);
    if (!skill) return;
    if (isSkillSelected(skill)) return;

    selectedSkills.push(skill);
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
    clearFieldError("skills-error");
  }

  function removeSkill(skill) {
    selectedSkills = selectedSkills.filter(function (selectedSkill) {
      return normalizeSkill(selectedSkill) !== normalizeSkill(skill);
    });
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
  }

  function renderSelectedChips() {
    if (!chipsSelectedEl) return;
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
    if (skillsHidden) {
      skillsHidden.value = selectedSkills.join(", ");
    }
  }

  updateQuickPickState();


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
    var rawText = skillsTextInput ? skillsTextInput.value.trim() : "";

    if (selectedSkills.length === 0 && (!skillsHidden || !skillsHidden.value.trim()) && !rawText) {
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

    if (skillsTextInput && skillsTextInput.value.trim()) {
      addSkill(skillsTextInput.value);
      skillsTextInput.value = "";
      hideSuggestions();
    }

    if (!validateForm()) return;

    setLoadingState(true);

    var payload = {
      skills:   (skillsHidden && skillsHidden.value.trim()) || (skillsTextInput ? skillsTextInput.value.trim() : ""),
      level:    document.getElementById("level").value,
      interest: document.getElementById("interest").value,
      time:     document.getElementById("time").value
    };

    fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
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
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline" : "none";

    if (isLoading) {
      resultsSection.style.display = "block";
      resultsLoadingEl.style.display = "block";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "none";
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } else {
      resultsLoadingEl.style.display = "none";
      resultsGrid.style.display = "grid";
    }
  }


  // ----------------------------------------------------------
  // Render result cards
  // ----------------------------------------------------------
  function renderResults(projects, message) {
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    resultsGrid.innerHTML = "";

    if (!projects || projects.length === 0) {
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";
      if (message && emptyMessageEl) emptyMessageEl.textContent = message;
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
    desc.textContent = truncate(project.description, 120);

    var tagsRow = document.createElement("div");
    tagsRow.className = "project-card-tags";

    (project.skills || []).slice(0, 2).forEach(function (skill) {
      tagsRow.appendChild(createTag(skill, "skill"));
    });

    var levelClass = "level " + (project.level || "").toLowerCase();
    tagsRow.appendChild(createTag(project.level, levelClass));
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

  // Visual component for tags
  function createTag(text, type) {
    var span = document.createElement("span");
    span.className = "project-tag project-tag--" + type;
    span.textContent = text;
    return span;
  }

  function truncate(text, maxLength) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

  // ----------------------------------------------------------
  // RESUME LEARNING INJECTION (Dashboard Widget UI)
  // ----------------------------------------------------------
  (function initResumeDashboard() {
    var progress = getProgress();
    
    if (progress.lastAccessedStep && progress.currentProjectId) {
      var mainFormWrapper = document.getElementById("recommend-form");
      if (!mainFormWrapper) return;
      
      var resumeCard = document.createElement("div");
      resumeCard.id = "resume-learning-card";
      resumeCard.style.cssText = "background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; padding: 24px; border-radius: 12px; margin-bottom: 32px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); text-align: left;";
      
      resumeCard.innerHTML = 
        '<div style="display: flex; flex-direction: column; md-flex-direction: row; justify-content: space-between; align-items: flex-start; gap: 16px;">' +
          '<div style="flex: 1;">' +
            '<span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; background: #86efac; color: #166534; padding: 4px 12px; border-radius: 9999px;">Continue Learning</span>' +
            '<h3 style="font-size: 20px; font-weight: 700; color: #14532d; margin-top: 12px; margin-bottom: 4px; font-family: Sora, sans-serif;">' + progress.lastAccessedStep.title + '</h3>' +
            '<p style="font-size: 14px; color: #166534; font-family: Inter, sans-serif;">Pick up exactly where you left off on your custom project roadmap.</p>' +
          '</div>' +
          '<div style="align-self: flex-start; margin-top: 4px;">' +
            '<a href="/project/' + progress.currentProjectId + '" class="btn-hero-primary" style="display: inline-block; padding: 12px 24px; font-size: 14px; text-decoration: none; font-weight: 600; border-radius: 8px; background: #15803d; color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">Jump Back In →</a>' +
          '</div>' +
        '</div>';
        
      mainFormWrapper.parentNode.insertBefore(resumeCard, mainFormWrapper);
    }
  })();

} // end isIndexPage


// ============================================================
// DETAIL PAGE
// ============================================================
if (isDetailPage) {

  var codePanel = document.getElementById("code-panel");
  var codePanelOverlay = document.getElementById("code-panel-overlay");
  var codeContentEl = document.getElementById("code-content");
  var codePanelFilename = document.getElementById("code-panel-filename");
  var btnViewCode = document.getElementById("btn-view-code");
  var btnViewCodeSm = document.getElementById("btn-view-code-sm");
  var btnClosePanel = document.getElementById("code-panel-close");

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
        if (codeContentEl) codeContentEl.textContent = data.code;
        codeFetched = true;
      })
      .catch(function () {
        if (codeContentEl) {
          codeContentEl.textContent = "Could not load starter code. Try downloading it instead.";
        }
      });
  }

  if (btnViewCode) btnViewCode.addEventListener("click", openCodePanel);
  if (btnViewCodeSm) btnViewCodeSm.addEventListener("click", openCodePanel);
  if (btnClosePanel) btnClosePanel.addEventListener("click", closeCodePanel);
  if (codePanelOverlay) codePanelOverlay.addEventListener("click", closeCodePanel);

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

    var copyIcon  = btnCopyCode.querySelector(".copy-icon");
    var checkIcon = btnCopyCode.querySelector(".check-icon");
    var btnLabel  = btnCopyCode.querySelector(".copy-btn-label");

    if (copyIcon)  copyIcon.style.display  = "none";
    if (checkIcon) checkIcon.style.display = "inline";
    if (btnLabel)  btnLabel.textContent    = "Copied!";
    btnCopyCode.classList.add("copied");
    btnCopyCode.disabled = true;

    if (copyToast) copyToast.classList.add("show");

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
    try { document.execCommand("copy"); showCopySuccess(); } catch (e) {}
    document.body.removeChild(ta);
  }

  // ----------------------------------------------------------
  // ROADMAP PROGRESS TRACKING INJECTION
  // ----------------------------------------------------------
  (function renderProjectProgressControls() {
    // Perfectly aligns with your project.html list structures
    var stepItems = document.querySelectorAll(".roadmap-step");
    if (stepItems.length === 0) return;

    var progress = getProgress();
    var currentProjectData = progress.projects[PROJECT_ID] || { steps: {} };

    // Inject the loading progress percentage card above Step 1
    var containerParent = stepItems[0].parentNode;
    var progressMetricWrapper = document.createElement("div");
    progressMetricWrapper.style.cssText = "background: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 28px; border: 1px solid #e2e8f0; text-align: left;";
    progressMetricWrapper.innerHTML = 
        '<div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; font-weight: 600; color: #334155; font-family: Sora, sans-serif;">' +
            '<span>Project Path Completion</span>' +
            '<span id="project-progress-text">0% Completed (0 steps done)</span>' +
        '</div>' +
        '<div style="background: #e2e8f0; border-radius: 9999px; height: 10px; width: 100%; overflow: hidden;">' +
            '<div id="project-progress-bar" style="background: #10b981; height: 100%; width: 0%; transition: width 0.4s ease;"></div>' +
        '</div>';
    
    containerParent.insertBefore(progressMetricWrapper, stepItems[0]);

    // Attach tracking select menus to your template elements dynamically
    stepItems.forEach(function(item, index) {
        var stepId = "step_" + index;
        
        // Correctly read the clean inner text from .roadmap-step-text wrapper
        var stepTitleEl = item.querySelector(".roadmap-step-text") || { textContent: "Step " + (index + 1) };
        var stepTitle = stepTitleEl.textContent.trim();
        var savedStatus = currentProjectData.steps[stepId] || "Not Started";

        var selectWrapper = document.createElement("div");
        selectWrapper.style.cssText = "margin-top: 12px; display: block; text-align: left;";
        selectWrapper.innerHTML = 
            '<select class="status-select-input" style="padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; border: 1px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; font-family: Inter, sans-serif;" ' +
                    'onchange="window.updateStepStatus(\'' + PROJECT_ID + '\', \'' + stepId + '\', \'' + stepTitle + '\', this.value, ' + stepItems.length + ')">' +
                '<option value="Not Started"' + (savedStatus === "Not Started" ? " selected" : "") + '>Not Started</option>' +
                '<option value="In Progress"' + (savedStatus === "In Progress" ? " selected" : "") + '>In Progress</option>' +
                '<option value="Completed"' + (savedStatus === "Completed" ? " selected" : "") + '>Completed</option>' +
            '</select>';

        // Append selector into the roadmap content layout container node
        var contentBlock = item.querySelector(".roadmap-content");
        if (contentBlock) {
            contentBlock.appendChild(selectWrapper);
        } else {
            item.appendChild(selectWrapper);
        }
    });

    // Fire state calculations immediately
    updateProgressBarUI(PROJECT_ID);
  })();

} // end isDetailPage  


// ============================================================
// GLOBAL PROGRESS MANAGEMENT STORAGE HOOKS (Shared Engine)
// ============================================================
var STORAGE_KEY = 'DevPath_Progress';

function getProgress() {
    try {
        var data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : { currentProjectId: null, lastAccessedStep: null, projects: {} };
    } catch (e) {
        return { currentProjectId: null, lastAccessedStep: null, projects: {} };
    }
}

function saveProgress(progressData) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(progressData));
    } catch (e) {
        console.error("Storage write error:", e);
    }
}

window.updateStepStatus = function(projectId, stepId, stepTitle, status, totalSteps) {
    var progress = getProgress();

    if (!progress.projects[projectId]) {
        progress.projects[projectId] = { completedCount: 0, totalCount: totalSteps, steps: {} };
    }

    progress.projects[projectId].steps[stepId] = status;

    if (status === 'In Progress' || status === 'Completed') {
        progress.currentProjectId = projectId;
        progress.lastAccessedStep = { id: stepId, title: stepTitle, projectId: projectId };
    }

    var steps = progress.projects[projectId].steps;
    var completedCount = 0;
    for (var key in steps) {
        if (steps.hasOwnProperty(key) && steps[key] === 'Completed') {
            completedCount++;
        }
    }
    
    progress.projects[projectId].completedCount = completedCount;
    progress.projects[projectId].totalCount = totalSteps;

    saveProgress(progress);
    updateProgressBarUI(projectId);
};

function updateProgressBarUI(projectId) {
    var progress = getProgress();
    var projectData = progress.projects[projectId];
    
    var progressBar = document.getElementById('project-progress-bar');
    var progressText = document.getElementById('project-progress-text');
    
    if (projectData && projectData.totalCount > 0) {
        var percent = Math.round((projectData.completedCount / projectData.totalCount) * 100) || 0;
        if (progressBar) progressBar.style.width = percent + '%';
        if (progressText) progressText.textContent = percent + '% Completed (' + projectData.completedCount + '/' + projectData.totalCount + ' steps)';
    }
}