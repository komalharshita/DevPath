/**
 * static/bookmarks.js
 * Quick-Save / Session-Restore utility for DevPath.
 *
 * Responsibilities
 * ----------------
 * 1. SAVED PROJECTS  – persist bookmarked project cards across browser sessions
 *    using the existing `devpathSavedProjects` key so the data stays compatible
 *    with what script.js already stores.
 *
 * 2. SESSION RESTORE – persist the last-used form values (skills, level,
 *    interest, time) so users never have to re-enter them after a refresh or
 *    accidental tab close.
 *
 * This file exposes a single global `DevPathBookmarks` object.
 * script.js does not need to be modified — it already calls getSavedProjects /
 * saveSavedProjects / renderSavedProjects which rely on the same storage key.
 *
 * Public API
 * ----------
 * DevPathBookmarks.restoreSession()   – called on DOMContentLoaded
 * DevPathBookmarks.saveSession()      – called on form change / submit
 * DevPathBookmarks.clearSession()     – called by the Clear Filters button
 * DevPathBookmarks.getSaved()         – returns array of saved project objects
 * DevPathBookmarks.isSaved(id)        – boolean
 * DevPathBookmarks.save(project)      – add a project
 * DevPathBookmarks.remove(id)         – remove a project
 * DevPathBookmarks.renderPanel()      – redraw the saved-projects panel
 */

var DevPathBookmarks = (function () {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* Constants                                                            */
  /* ------------------------------------------------------------------ */
  var SAVED_KEY   = "devpathSavedProjects";   // shared with script.js
  var SESSION_KEY = "devpathSessionForm";

  /* ------------------------------------------------------------------ */
  /* Safe localStorage helpers                                            */
  /* ------------------------------------------------------------------ */
  function lsGet(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch (err) {
      return null;
    }
  }

  function lsSet(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (err) {
      console.warn("[DevPathBookmarks] localStorage write failed:", err);
      return false;
    }
  }

  /* ------------------------------------------------------------------ */
  /* Saved Projects                                                        */
  /* ------------------------------------------------------------------ */
  function getSaved() {
    var data = lsGet(SAVED_KEY);
    return Array.isArray(data) ? data : [];
  }

  function isSaved(projectId) {
    return getSaved().some(function (p) {
      return String(p.id) === String(projectId);
    });
  }

  function save(project) {
    if (!project || !project.id) return false;
    var saved = getSaved();
    if (saved.some(function (p) { return String(p.id) === String(project.id); })) {
      return false; // already saved
    }
    saved.unshift({
      id:     project.id,
      title:  project.title  || "Project " + project.id,
      level:  project.level  || "",
      time:   project.time   || "",
      skills: Array.isArray(project.skills) ? project.skills.slice(0, 4) : []
    });
    lsSet(SAVED_KEY, saved);
    renderPanel();
    return true;
  }

  function remove(projectId) {
    var saved = getSaved().filter(function (p) {
      return String(p.id) !== String(projectId);
    });
    lsSet(SAVED_KEY, saved);
    renderPanel();
    // Sync any visible save buttons for this project
    document.querySelectorAll("[data-save-project-id='" + projectId + "']").forEach(function (btn) {
      btn.classList.remove("saved");
      btn.setAttribute("aria-pressed", "false");
      btn.setAttribute("aria-label", "Save project");
      _setButtonContent(btn, false);
    });
  }

  function toggle(project, button) {
    if (isSaved(project.id)) {
      remove(project.id);
    } else {
      save(project);
      if (button) {
        button.classList.add("saved");
        button.setAttribute("aria-pressed", "true");
        button.setAttribute("aria-label", "Remove saved project");
        _setButtonContent(button, true);
      }
    }
  }

  /* Build the bookmark icon + label content for the save button */
  function _setButtonContent(button, saved) {
    button.innerHTML =
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="' + (saved ? "currentColor" : "none") + '" ' +
      'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>' +
      "</svg>" +
      (saved ? " Saved" : " Save Project");
  }

  /* ------------------------------------------------------------------ */
  /* Saved Projects Panel                                                  */
  /* ------------------------------------------------------------------ */
  function renderPanel() {
    var panel = document.getElementById("saved-projects-panel");
    var list  = document.getElementById("saved-projects-list");
    var count = document.getElementById("saved-projects-count");
    if (!list || !count || !panel) return;

    var saved = getSaved();
    count.textContent = saved.length === 1 ? "1 project saved" : `${saved.length} projects saved`;
    // Show panel only when there is at least one saved project
    panel.style.display = saved.length ? "block" : "none";

    list.textContent = "";

    if (!saved.length) {
      var empty = document.createElement("p");
      empty.className = "saved-projects-empty";
      empty.textContent = "No saved projects yet. Click \u201CSave Project\u201D on any result card.";
      list.appendChild(empty);
      return;
    }

    saved.forEach(function (project) {
      var item = document.createElement("article");
      item.className = "saved-project-item";

      var titleLink = document.createElement("a");
      titleLink.href = "/project/" + project.id;
      titleLink.textContent = project.title;

      var meta = document.createElement("span");
      meta.textContent = [project.level, project.time].filter(Boolean).join(" \u00B7 ");

      var removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "saved-project-remove";
      removeBtn.setAttribute("aria-label", "Remove " + project.title + " from saved projects");
      removeBtn.textContent = "Remove";
      removeBtn.addEventListener("click", function () {
        remove(project.id);
      });

      item.appendChild(titleLink);
      item.appendChild(meta);
      item.appendChild(removeBtn);
      list.appendChild(item);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Session Persistence                                                   */
  /* ------------------------------------------------------------------ */

  /**
   * Save current form values to localStorage.
   * Skills are read from the hidden input (comma-separated) which script.js
   * keeps in sync via syncSkillsHiddenInput().
   */
  function saveSession() {
    var skillsHidden = document.getElementById("skills");
    var level        = document.getElementById("level");
    var interest     = document.getElementById("interest");
    var time         = document.getElementById("time");

    if (!skillsHidden && !level && !interest && !time) return;

    lsSet(SESSION_KEY, {
      skills:   skillsHidden ? skillsHidden.value : "",
      level:    level        ? level.value        : "",
      interest: interest     ? interest.value     : "",
      time:     time         ? time.value         : ""
    });
  }

  /**
   * Restore previously saved form values on page load.
   * Skills are re-added via the global window.addSkill() exposed by script.js.
   */
  function restoreSession() {
    var session = lsGet(SESSION_KEY);
    if (!session || typeof session !== "object") return;

    // Restore skills: split comma-separated string, add each via script.js helper
    var rawSkills = (session.skills || "").trim();
    if (rawSkills) {
      // window.addSkill is defined by script.js; it deduplicates and updates UI
      var skillList = rawSkills.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
      skillList.forEach(function (skill) {
        if (typeof window.addSkill === "function") window.addSkill(skill);
      });
    }

    // Restore select values
    _setSelectValue("level",    session.level);
    _setSelectValue("interest", session.interest);
    _setSelectValue("time",     session.time);
  }

  function _setSelectValue(id, value) {
    if (!value) return;
    var el = document.getElementById(id);
    if (!el) return;
    // Only restore if the option actually exists in the DOM
    var options = Array.prototype.slice.call(el.options);
    var match = options.some(function (opt) { return opt.value === value; });
    if (match) el.value = value;
  }

  /** Remove the persisted session (called by Clear Filters). */
  function clearSession() {
    try {
      localStorage.removeItem(SESSION_KEY);
    } catch (err) {}
  }

  /* ------------------------------------------------------------------ */
  /* Auto-wire on DOMContentLoaded                                         */
  /* ------------------------------------------------------------------ */
  document.addEventListener("DOMContentLoaded", function () {
    // Restore session after script.js has run (it runs synchronously before
    // this callback fires, so window.addSkill is already defined).
    restoreSession();
    renderPanel();

    // Save session whenever the user changes a form field
    ["level", "interest", "time"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("change", saveSession);
    });

    // Save session when skills hidden input changes (dispatched by script.js)
    var skillsHidden = document.getElementById("skills");
    if (skillsHidden) {
      skillsHidden.addEventListener("change", saveSession);
    }

    // Also save on form submit so the values are definitely persisted
    var form = document.getElementById("recommend-form");
    if (form) {
      form.addEventListener("submit", function () {
        saveSession();
      }, true); // capture phase so it runs before script.js submit handler
    }

    // Clear session when the Clear Filters button is clicked
    var clearBtn = document.getElementById("clear-filters-btn");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        clearSession();
        renderPanel();
      });
    }

    // Wire up detail page save button
    var detailSaveBtn = document.getElementById("btn-save-project-detail");
    if (detailSaveBtn && typeof PROJECT_ID !== "undefined") {
      var projectObj = {
        id: PROJECT_ID,
        title: typeof PROJECT_TITLE !== "undefined" ? PROJECT_TITLE : "Project " + PROJECT_ID,
        level: typeof PROJECT_LEVEL !== "undefined" ? PROJECT_LEVEL : "",
        time: typeof PROJECT_TIME !== "undefined" ? PROJECT_TIME : "",
        skills: typeof PROJECT_SKILLS !== "undefined" && Array.isArray(PROJECT_SKILLS) ? PROJECT_SKILLS : []
      };

      var savedState = isSaved(PROJECT_ID);
      detailSaveBtn.classList.toggle("saved", savedState);
      detailSaveBtn.setAttribute("aria-pressed", savedState ? "true" : "false");
      _setButtonContent(detailSaveBtn, savedState);

      detailSaveBtn.addEventListener("click", function () {
        toggle(projectObj, detailSaveBtn);
      });
    }
  });

  /* ------------------------------------------------------------------ */
  /* Public API                                                            */
  /* ------------------------------------------------------------------ */
  return {
    getSaved:       getSaved,
    isSaved:        isSaved,
    save:           save,
    remove:         remove,
    toggle:         toggle,
    renderPanel:    renderPanel,
    saveSession:    saveSession,
    restoreSession: restoreSession,
    clearSession:   clearSession,
    setButtonContent: _setButtonContent
  };
}());
