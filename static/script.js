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
var isIndexPage = !!document.getElementById("recommend-form");
var isDetailPage = typeof PROJECT_ID !== "undefined";


// ============================================================
// Mobile navigation toggle (runs on all pages)
// ============================================================
(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu = document.getElementById("nav-mobile-menu");

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
  var skillsTextInput = document.getElementById("skills-input");
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
      "Blockchain", "UI/UX Design", "Game Development", "CI/CD", "REST API", "GraphQL"
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

  // Add skill on quick-pick chip click
  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      addSkill(chip.getAttribute("data-skill"));
      hideSuggestions();
      skillsTextInput.value = "";
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

    // Block duplicate entries (case-insensitive)
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
      // Show the results section with only the loading indicator visible
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

    // Title
    var title = document.createElement("h3");
    title.className = "project-card-title";
    title.textContent = project.title;

    // Description (truncated for visual consistency)
    var desc = document.createElement("p");
    desc.className = "project-card-desc";
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

   } // end isIndexPage

   // ============================================================
   // SHAREABLE URL FEATURE
   // ============================================================
   function initShareFeature() {
     // DOM elements
     const shareBtn = document.getElementById('share-btn');
     const shareToast = document.getElementById('share-toast');
     const resultsSection = document.getElementById('results-section');
     
     if (!shareBtn || !shareToast) return;
     
     let toastTimeout = null;
     
     // Show share button when results are loaded
     function showShareButton() {
       shareBtn.style.display = 'inline-block';
     }
     
     // Hide share button
     function hideShareButton() {
       shareBtn.style.display = 'none';
     }
     
     // Generate shareable URL from current form state
     function generateShareUrl() {
       const baseUrl = window.location.origin + window.location.pathname;
       const params = new URLSearchParams();
       
       // Get skills
       const skillsInput = document.getElementById('skills');
       if (skillsInput && skillsInput.value.trim()) {
         params.append('skills', skillsInput.value.trim());
       }
       
       // Get level
       const levelSelect = document.getElementById('level');
       if (levelSelect && levelSelect.value) {
         params.append('level', levelSelect.value);
       }
       
       // Get interest
       const interestSelect = document.getElementById('interest');
       if (interestSelect && interestSelect.value) {
         params.append('interest', interestSelect.value);
       }
       
       // Get time
       const timeSelect = document.getElementById('time');
       if (timeSelect && timeSelect.value) {
         params.append('time', timeSelect.value);
       }
       
       // Construct final URL
       const queryString = params.toString();
       return queryString ? `${baseUrl}?${queryString}` : baseUrl;
     }
     
     // Copy URL to clipboard and show toast
     async function copyShareUrl() {
       const shareUrl = generateShareUrl();
       
       try {
         await navigator.clipboard.writeText(shareUrl);
         showToast();
       } catch (err) {
         // Fallback for older browsers
         const textarea = document.createElement('textarea');
         textarea.value = shareUrl;
         document.body.appendChild(textarea);
         textarea.select();
         document.execCommand('copy');
         document.body.removeChild(textarea);
         showToast();
       }
     }
     
     // Show toast notification
     function showToast() {
       shareToast.classList.add('show');
       
       // Clear previous timeout
       if (toastTimeout) {
         clearTimeout(toastTimeout);
       }
       
       // Hide toast after 2 seconds
       toastTimeout = setTimeout(() => {
         shareToast.classList.remove('show');
       }, 2000);
     }
     
     // Restore form state from URL parameters
     function restoreFormState() {
       const params = new URLSearchParams(window.location.search);
       const hasParams = params.toString().length > 0;
       
       if (!hasParams) return;
       
       // Restore skills
       const skillsParam = params.get('skills');
       if (skillsParam) {
         // Clear existing skills
         selectedSkills = [];
         renderSelectedChips();
         
         // Add skills from param (comma-separated)
         const skillsArray = skillsParam.split(',').map(skill => skill.trim()).filter(skill => skill);
         skillsArray.forEach(skill => {
           addSkill(skill);
         });
         
         // Sync hidden input
         syncSkillsHiddenInput();
       }
       
       // Restore level
       const levelParam = params.get('level');
       if (levelParam) {
         const levelSelect = document.getElementById('level');
         if (levelSelect) {
           levelSelect.value = levelParam;
         }
       }
       
       // Restore interest
       const interestParam = params.get('interest');
       if (interestParam) {
         const interestSelect = document.getElementById('interest');
         if (interestSelect) {
           interestSelect.value = interestParam;
         }
       }
       
       // Restore time
       const timeParam = params.get('time');
       if (timeParam) {
         const timeSelect = document.getElementById('time');
         if (timeSelect) {
           timeSelect.value = timeParam;
         }
       }
       
       // Trigger automatic recommendation generation
       // Small delay to ensure DOM is ready
       setTimeout(() => {
         if (validateForm()) {
           form.dispatchEvent(new Event('submit'));
         }
       }, 100);
     }
     
     // Event listeners
     shareBtn.addEventListener('click', copyShareUrl);
     
     // Initialize
     // Show share button when results are loaded
     const originalRenderResults = renderResults;
     renderResults = function(projects, message) {
       originalRenderResults.call(this, projects, message);
       if (projects && projects.length > 0) {
         showShareButton();
       } else {
         hideShareButton();
       }
     };
     
     // Restore state on page load
     restoreFormState();
   }
   
   // Initialize share feature on index page
   if (isIndexPage) {
     initShareFeature();
   }
 


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
        if (codeContentEl) codeContentEl.textContent = data.code;
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
