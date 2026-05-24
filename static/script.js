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
  
  // Clear Filters Button Functionality
  var clearFiltersBtn = document.getElementById("clear-filters-btn");
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function() {
        var recommendForm = document.getElementById("recommend-form");
        if (recommendForm) {
            // 1. Reset standard form dropdowns and fields
            recommendForm.reset();
            
            // 2. Clear out the internal JavaScript array tracker completely
            selectedSkills = [];
            
            // 3. Clear the hidden inputs and visual chips using the file's own variables
            if (skillsHidden) skillsHidden.value = "";
            if (chipsSelectedEl) chipsSelectedEl.innerHTML = "";
            if (skillsTextInput) {
                skillsTextInput.value = "";
                skillsTextInput.focus(); // Place cursor back on input
            }
            
            // 4. Hide autocomplete suggestions if any are open
            var suggestionsBox = document.getElementById("skills-suggestions");
            if (suggestionsBox) suggestionsBox.innerHTML = "";

            // 5. Reset quick-pick chip visual active states if they have any
            if (quickPickChips) {
                quickPickChips.forEach(function(chip) {
                    chip.classList.remove("active", "selected");
                });
            }
        }
    });
  }


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

  function initSkillStripMarquee() {
    var marquee = document.querySelector(".skill-strip-marquee");
    var track = marquee && marquee.querySelector(".skill-strip-track");

    if (!marquee || !track || track.querySelector(".skill-strip-items[data-marquee-clone='true']")) {
      return;
    }

    var clone = track.querySelector(".skill-strip-items").cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    clone.setAttribute("data-marquee-clone", "true");
    track.appendChild(clone);
  }

  availableSkills = availableSkills.filter(function (skill, index, list) {
    return typeof skill === "string" && skill.trim() &&
      list.findIndex(function (item) {
        return item.toLowerCase() === skill.toLowerCase();
      }) === index;
  });

  if (suggestionsDiv) {
    suggestionsDiv.setAttribute("role", "listbox");
  }

  initSkillStripMarquee();

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
  // when the user types a skill and hits Enter, add it we intercept Enter here so it doesn't accidentally submit the whole form
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


  document.addEventListener("click", function (evt) {
    if (skillWrap && !skillWrap.contains(evt.target)) {
      hideSuggestions();
    }
  });

  //add a skill to the list if it's not empty or a duplicate
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

  // remove a skill from the list and update the UI accordingly
  function removeSkill(skill) {
    selectedSkills = selectedSkills.filter(function (selectedSkill) {
      return normalizeSkill(selectedSkill) !== normalizeSkill(skill);
    });
    renderSelectedChips();
    syncSkillsHiddenInput();
    updateQuickPickState();
  }

  // recreate the selected skills chips based on the current array
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
    if (!skillsHidden){
      var skillsHidden = document.getElementById("skills");
    }
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

    requestAnimationFrame(function () {
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
  });

  function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.setAttribute("aria-busy", isLoading);
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline-flex" : "none";

    if (isLoading) {
      resultsSection.style.display = "block";
      resultsLoadingEl.style.display = "block";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "none";
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
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    resultsGrid.innerHTML = "";

    if (!projects || projects.length === 0) {
      resultsGrid.style.display = "none";
      
      if (resultsEmptyEl) resultsEmptyEl.style.display = "block"; 
      
      if (emptyMessageEl) {
        emptyMessageEl.innerHTML = `
          ${message || "No projects match your current inputs."}<br><br>
          <strong>Try adding popular alternative skills</strong> like Python, JavaScript, HTML, or CSS to see more matching repositories!
        `;
      }
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
        if (codeContentEl) {
          codeContentEl.textContent = "";
          renderCodeWithLineNumbers(data.code).forEach(function (row) {
            codeContentEl.appendChild(row);
          });
        }
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

    var copyIcon  = btnCopyCode.querySelector(".copy-icon");
    var checkIcon = btnCopyCode.querySelector(".check-icon");
    var btnLabel = btnCopyCode.querySelector(".copy-btn-label");

    if (copyIcon) copyIcon.style.display = "none";
    if (checkIcon) checkIcon.style.display = "inline";
    if (btnLabel) btnLabel.textContent = "Copied!";
    btnCopyCode.classList.add("copied");
    btnCopyCode.disabled = true;

    if (copyToast) {
      copyToast.classList.add("show");
    }

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
  openModalBtn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
      githubInput.focus();
  });

  const closeGithubModal = () => {
      modal.classList.remove('active');
      githubInput.value = '';
      errorMsg.textContent = '';
  };

  closeModalBtn.addEventListener('click', closeGithubModal);

  modal.addEventListener('click', (e) => {
      if (e.target === modal) closeGithubModal();
  });

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
}

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