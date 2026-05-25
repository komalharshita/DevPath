// script.js — DevPath client-side logic

var isIndexPage = !!document.getElementById("recommend-form");
var isDetailPage = typeof PROJECT_ID !== "undefined";

var modal = document.getElementById("github-modal-overlay");
var openModalBtn = document.getElementById("btn-show-github");
var closeModalBtn = document.getElementById("btn-close-github");
var fetchBtn = document.getElementById("btn-fetch-github");
var githubInput = document.getElementById("github-username");
var errorMsg = document.getElementById("github-modal-error");

// Mobile navigation
(function initMobileNav() {
  var toggle = document.getElementById("nav-mobile-toggle");
  var menu = document.getElementById("nav-mobile-menu");

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
      toggle.setAttribute("aria-expanded", "false");
    });
  });
})();

// INDEX PAGE
if (isIndexPage) {
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

  var selectedSkills = [];

  var clearFiltersBtn = document.getElementById("clear-filters-btn");
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function () {
      form.reset();
      selectedSkills = [];

      if (skillsHidden) skillsHidden.value = "";
      if (chipsSelectedEl) chipsSelectedEl.innerHTML = "";
      if (skillsTextInput) skillsTextInput.value = "";

      var suggestionsBox = document.getElementById("skills-suggestions");
      if (suggestionsBox) suggestionsBox.innerHTML = "";

      quickPickChips.forEach(function (chip) {
        chip.classList.remove("active", "selected");
        chip.setAttribute("aria-pressed", "false");
      });
    });
  }

  var availableSkills = [];

  if (typeof skills !== "undefined" && Array.isArray(skills) && skills.length > 0) {
    availableSkills = skills.map(function (s) {
      return s.label;
    });
  } else {
    availableSkills = [
      "Python", "JavaScript", "Java", "C++", "HTML", "CSS", "React", "Node.js",
      "Django", "Flask", "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "Git",
      "C#", "Ruby", "PHP", "Go", "Swift", "TypeScript", "Angular", "Vue.js",
      "Spring", "Flutter", "TensorFlow", "PyTorch", "Data Science",
      "Machine Learning", "Artificial Intelligence", "DevOps", "Cybersecurity",
      "Blockchain", "UI/UX Design", "Game Development", "CI/CD", "REST API",
      "GraphQL", "Rust", "Kotlin"
    ];
  }

  var suggestionsDiv = document.getElementById("skills-suggestions");
  var skillWrap = document.getElementById("skill-input-wrap");
  var visibleSuggestions = [];
  var activeSuggestionIndex = -1;

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

  function hideSuggestions() {
    visibleSuggestions = [];
    activeSuggestionIndex = -1;

    if (suggestionsDiv) {
      suggestionsDiv.style.display = "none";
      suggestionsDiv.innerHTML = "";
    }

    if (skillsTextInput) {
      skillsTextInput.setAttribute("aria-expanded", "false");
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
      item.setAttribute("aria-selected", "false");

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
    skillsTextInput.setAttribute("aria-expanded", "true");
  }

  function updateQuickPickState() {
    quickPickChips.forEach(function (chip) {
      var skill = chip.getAttribute("data-skill") || "";
      var isActive = isSkillSelected(skill);
      chip.classList.toggle("active", isActive);
      chip.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }

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
          activeSuggestionIndex =
            activeSuggestionIndex <= 0
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
      setTimeout(function () {
        hideSuggestions();
      }, 150);
    });
  }

  quickPickChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var skill = chip.getAttribute("data-skill");

      if (isSkillSelected(skill)) {
        removeSkill(skill);
      } else {
        addSkill(skill);
      }

      hideSuggestions();
      if (skillsTextInput) skillsTextInput.value = "";
    });
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

  updateQuickPickState();

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
        skills: skillsHidden.value.trim(),
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
            if (generalErr) generalErr.textContent = data.error;
            return;
          }

          renderResults(data.projects || [], data.message);
        })
        .catch(function (err) {
          setLoadingState(false);

          var generalErr = document.getElementById("form-error-general");
          if (generalErr) {
            generalErr.textContent = "Something went wrong. Please try again.";
          }

          console.error("API request failed:", err);
        });
    });
  });

  function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.setAttribute("aria-busy", isLoading ? "true" : "false");

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
    }
  }

  function renderResults(projects, message) {
    resultsSection.style.display = "block";
    resultsLoadingEl.style.display = "none";
    resultsGrid.innerHTML = "";

    if (!projects || projects.length === 0) {
      resultsGrid.style.display = "none";
      resultsEmptyEl.style.display = "block";

      if (message && emptyMessageEl) {
        emptyMessageEl.textContent = message;
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
    span.textContent = text || "";
    return span;
  }

  function truncate(text, maxLength) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  }

  // GitHub modal
  if (
    openModalBtn &&
    closeModalBtn &&
    modal &&
    githubInput &&
    fetchBtn &&
    errorMsg
  ) {
    openModalBtn.addEventListener("click", function (e) {
      e.preventDefault();
      modal.classList.add("active");
      githubInput.focus();
    });

    function closeGithubModal() {
      modal.classList.remove("active");
      githubInput.value = "";
      errorMsg.textContent = "";
    }

    closeModalBtn.addEventListener("click", closeGithubModal);

    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeGithubModal();
    });

    fetchBtn.addEventListener("click", async function () {
      var username = githubInput.value.trim();
      if (!username) return;

      fetchBtn.disabled = true;
      fetchBtn.textContent = "Syncing...";

      try {
        var response = await fetch("https://api.github.com/users/" + username + "/repos");

        if (!response.ok) {
          throw new Error("Failed to fetch skills");
        }

        var repos = await response.json();
        var langs = [...new Set(repos.map(function (r) {
          return r.language;
        }).filter(Boolean))];

        if (langs.length > 0) {
          langs.forEach(function (lang) {
            addSkill(lang);
          });

          closeGithubModal();
        } else {
          errorMsg.textContent = "No public languages found.";
        }
      } catch (err) {
        errorMsg.textContent = err.message || "Failed to fetch skills";
      } finally {
        fetchBtn.disabled = false;
        fetchBtn.textContent = "Fetch Skills";
      }
    });
  }
}

// DETAIL PAGE
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
      .then(function (res) {
        return res.json();
      })
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

  function renderCodeWithLineNumbers(code) {
    return code.split("\n").map(function (line, index) {
      var row = document.createElement("div");
      row.className = "code-line";

      var lineNumber = document.createElement("span");
      lineNumber.className = "line-number";
      lineNumber.textContent = index + 1;

      var lineContent = document.createElement("span");
      lineContent.className = "line-content";
      lineContent.textContent = line;

      row.appendChild(lineNumber);
      row.appendChild(lineContent);

      return row;
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

  var btnCopyCode = document.getElementById("btn-copy-code");
  var copyToast = document.getElementById("copy-toast");
  var toastTimeout = null;

  function showCopySuccess() {
    if (!btnCopyCode) return;

    var copyIcon = btnCopyCode.querySelector(".copy-icon");
    var checkIcon = btnCopyCode.querySelector(".check-icon");
    var btnLabel = btnCopyCode.querySelector(".copy-btn-label");

    if (copyIcon) copyIcon.style.display = "none";
    if (checkIcon) checkIcon.style.display = "inline";
    if (btnLabel) btnLabel.textContent = "Copied!";

    btnCopyCode.classList.add("copied");
    btnCopyCode.disabled = true;

    if (copyToast) copyToast.classList.add("show");

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
            .map(function (el) {
              return el.textContent;
            })
            .join("\n")
        : "";

      if (!code || code === "Loading..." || code === "Loading starter code...") return;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code)
          .then(showCopySuccess)
          .catch(function () {
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

    try {
      document.execCommand("copy");
      showCopySuccess();
    } catch (e) {}

    document.body.removeChild(ta);
  }
}

// Scroll-to-top button
var SCROLL_THRESHOLD = 300;
var scrollTopBtn = document.getElementById("scroll-top-btn");

function handleScroll() {
  if (!scrollTopBtn) return;

  if (window.pageYOffset > SCROLL_THRESHOLD) {
    scrollTopBtn.classList.add("visible");
  } else {
    scrollTopBtn.classList.remove("visible");
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

if (scrollTopBtn) {
  window.addEventListener("scroll", handleScroll);
  scrollTopBtn.addEventListener("click", scrollToTop);
}