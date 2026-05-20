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

  // Function to track skill selection on the server
  function trackSkillOnServer(skillLabel) {
    fetch("/api/track-skill", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ skill: skillLabel })
    })
    .catch(function (error) {
      console.warn("Failed to track skill on server:", error);
      // Silently fail - don't break user experience if tracking fails
    });
  }

  // Function to get the top 5 skills from the server
  function loadTopSkillsFromServer(callback) {
    fetch("/api/top-skills")
      .then(function (response) {
        if (!response.ok) throw new Error("Failed to fetch top skills");
        return response.json();
      })
      .then(function (data) {
        callback(data.skills || []);
      })
      .catch(function (error) {
        console.warn("Failed to load top skills from server:", error);
        // Fall back to default skills if server request fails
        callback([]);
      });
  }

  // Function to render the top 5 skills dynamically using server data
  function renderDynamicTopSkills() {
    var chipsContainer = document.getElementById("skill-chips-available");
    if (!chipsContainer) return;

    loadTopSkillsFromServer(function (topSkills) {
      chipsContainer.innerHTML = "";

      // If there are no top skills from server, show a default set of popular skills
      if (topSkills.length === 0) {
        topSkills = [
          { label: "Python" },
          { label: "JavaScript" },
          { label: "HTML" },
          { label: "CSS" },
          { label: "React" }
        ];
      }

      topSkills.forEach(function (skill) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "skill-chip";
        btn.setAttribute("data-skill", skill.label);
        btn.textContent = skill.label;

        btn.addEventListener("click", function () {
          var skillLabel = btn.getAttribute("data-skill");
          var isAlreadySelected = selectedSkills.some(function (s) {
            return s.toLowerCase() === skillLabel.toLowerCase();
          });

          if (isAlreadySelected) {
            removeSkill(skillLabel);
          } else {
            addSkill(skillLabel);
          }
          hideSuggestions();
          skillsTextInput.value = "";
        });

        chipsContainer.appendChild(btn);
      });

      updateQuickPickState();
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

  // Dynamic skill chips are now rendered by renderDynamicTopSkills()
  // Event listeners for chips are added in renderDynamicTopSkills()


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
    // Clean up any extra spaces and match to canonical skill name
    var skill = getCanonicalSkill(rawSkill);
    // Nothing to add if string is empty after trimming
    if (!skill) return;

    // Block duplicate entries (case-insensitive)
    if (isSkillSelected(skill)) return;

    selectedSkills.push(skill);
    
    // Track the skill selection on the server
    trackSkillOnServer(skill);
    
    renderSelectedChips();
    syncSkillsHiddenInput();
    renderDynamicTopSkills();
    updateQuickPickState();
    // Once a skill is added, remove the "please add a skill" error if it was showing
    clearFieldError("skills-error");
  }

  // remove a skill from the list and update the UI accordingly
  function removeSkill(skill) {
    // Rebuild the array without the skill that was just removed
    selectedSkills = selectedSkills.filter(function (selectedSkill) {
      return normalizeSkill(selectedSkill) !== normalizeSkill(skill);
    });
    renderSelectedChips();
    syncSkillsHiddenInput();
    renderDynamicTopSkills();
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
    if (!skillsHidden){
      var skillsHidden = document.getElementById("skills");
    }
    // Keep the hidden <input> in sync for form serialisation
    // The API expects a comma-separated string, so join the array that way
    skillsHidden.value = selectedSkills.join(", ");
  }

  // Initialize the dynamic top skills rendering
  renderDynamicTopSkills();


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

  form.addEventListener("submit", function (evt) {
    evt.preventDefault(); //stop the browser from reloading the page on form submit
    clearAllErrors()
    
    if (skillsTextInput.value.trim()) {
      addSkill(skillsTextInput.value);
      skillsTextInput.value = "";
      hideSuggestions();
    }

    if (!validateForm()) return; //stop - anything missing/invalid

    setLoadingState(true);

    // Allow browser to paint spinner before request starts
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
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {

          setLoadingState(false);

          if (data.error) {
            var generalErr = document.getElementById("form-error-general");

            if (generalErr) {
              generalErr.textContent = data.error;
            }

            return;
          }

          renderResults(data.projects || [], data.message);
        })
        .catch(function () {

          setLoadingState(false);
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
      body:    JSON.stringify(payload) //convert object to json string
    })
      .then(function (res) { return res.json(); }) //parse the response as JSON
      .then(function (data) {
        setLoadingState(false);

          var generalErr = document.getElementById("form-error-general");

          if (generalErr) {
            generalErr.textContent =
              "Something went wrong. Please try again.";
          }
        });
    });
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

  // Manages the loading state of the form and results section(whats visible or not)
  function setLoadingState(isLoading) {
    // Disable the button so the user can't accidentally submit twice
    submitBtn.disabled = isLoading;
    submitBtn.setAttribute("aria-busy", isLoading);
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline-flex" : "none";
    btnLabel.style.display = isLoading ? "none" : "inline";
    btnLoading.style.display = isLoading ? "inline" : "none";

    if (isLoading) {
      // Show the results section with only the loading indicator visible
      resultsSection.style.display = "block";
      resultsLoadingEl.style.display = "block";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "none";
      // Scroll down so the user can see the spinner without manually scrolling
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

    if (!projects || projects.length === 0) {
      resultsGrid.style.display     = "none";
      resultsEmptyEl.style.display  = "block";
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";
      if (message && emptyMessageEl) emptyMessageEl.textContent = message;
    if (!projects || projects.length === 0) { //if no projects returned from api, show the "no results" message and hide the grid
      resultsGrid.style.display      = "none";
      resultsEmptyEl.style.display   = "block";
      if (message && emptyMessageEl) emptyMessageEl.textContent = message; //if api sent back a message (e.g. "no projects found matching your criteria"), show that 
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

  // builds one project card as a DOM element and returns it
  // the card has title, short description, tags and link
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
    // Cut description to 120 chars so all cards stay the same height
    desc.textContent = truncate(project.description, 120);

    // Tags row
    var tagsRow = document.createElement("div");
    tagsRow.className = "project-card-tags";

    // Show the first two skills as tags
    (project.skills || []).slice(0, 2).forEach(function (skill) {
      tagsRow.appendChild(createTag(skill, "skill"));
    });

    // Level tag (colour-coded via CSS class)
    // Lowercase so it matches the CSS class names like "level beginner", "level advanced"
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
    link.href = "/project/" + project.id; //each project has a unique id

    footer.appendChild(link);

    // Assemble the card in order
    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(tagsRow);
    card.appendChild(footer);

    return card;
  }

  // helper to create a coloured tag element (used for skills, level, time tags on the cards)
  function createTag(text, type) {
    var span = document.createElement("span");
    // The type becomes a BEM modifier so CSS can style each tag differently
    span.className = "project-tag project-tag--" + type;
    span.textContent = text;
    return span;
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
    var btnLabel = btnCopyCode.querySelector(".copy-btn-label");

    if (copyIcon) copyIcon.style.display = "none";
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
}

/* ---- Scroll-to-top button ---- */

/* Show the button only when the user has scrolled more than 300px */
var SCROLL_THRESHOLD = 300;

/* Get the button element; guard against pages that do not have it */
var scrollTopBtn = document.getElementById('scroll-top-btn');

/* Add or remove the .visible class based on scroll position */
function handleScroll() {
  if (!scrollTopBtn) return;
  if (window.pageYOffset > SCROLL_THRESHOLD) {
    scrollTopBtn.classList.add('visible');
  } else {
    scrollTopBtn.classList.remove('visible');
  }
}

/* Smooth-scroll to the very top of the page */
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* Only wire up listeners if the button exists on this page */
if (scrollTopBtn) {
    window.addEventListener('scroll', handleScroll);
    scrollTopBtn.addEventListener('click', scrollToTop);
}
