// static/auth.js
// Auth + dashboard for DevPath.
// Depends on script.js (window.progress, saveProgressState, etc) and bookmarks.js.
// Visual styling lives in style.css under "SECTION: AUTH" — this file only
// toggles classes, it does not set inline styles.

(function () {
  "use strict";

  var AUTH_TOKEN_KEY = "devpathAuthToken";
  var AUTH_USER_KEY = "devpathAuthUser";
  var AUTH_PATH_KEY = "devpathAuthPathId";

  // Read a value from localStorage, swallowing any access errors.
  function lsGet(k) {
    try {
      return localStorage.getItem(k);
    } catch (e) {
      return null;
    }
  }
  // Write a value to localStorage, swallowing any access errors.
  function lsSet(k, v) {
    try {
      localStorage.setItem(k, v);
    } catch (e) {}
  }
  // Remove a value from localStorage, swallowing any access errors.
  function lsDel(k) {
    try {
      localStorage.removeItem(k);
    } catch (e) {}
  }

  // Return the current session token, or null if signed out.
  function getToken() {
    return lsGet(AUTH_TOKEN_KEY);
  }
  // Return the current signed-in username, or null.
  function getUser() {
    return lsGet(AUTH_USER_KEY);
  }
  // Return the server-side learning-path ID tied to this account.
  function getPathId() {
    return lsGet(AUTH_PATH_KEY);
  }
  // Return true when a session token is present.
  function isLoggedIn() {
    return !!getToken();
  }

  // Expose so other scripts (e.g. bookmarks.js) can check sign-in state.
  window.authIsLoggedIn = isLoggedIn;

  // ---- toast ----

  // Create the toast element once, appended to the document body.
  function injectToast() {
    var el = document.createElement("div");
    el.id = "auth-toast";
    el.className = "auth-toast";
    document.body.appendChild(el);
  }

  // Show a brief confirmation message at the bottom of the screen.
  function showToast(message) {
    var toast = document.getElementById("auth-toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(function () {
      toast.classList.remove("show");
    }, 2800);
  }

  // ---- server progress sync ----

  // Push the full progress object to the server, creating the path first
  // if it doesn't exist yet (404 on PUT means "not created", so retry as POST).
  function pushProgressToServer(data) {
    var token = getToken(),
      pathId = getPathId();
    if (!token || !pathId) return;
    fetch("/api/learning-path/" + pathId, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Learning-Path-Token": token,
      },
      body: JSON.stringify(data),
    })
      .then(function (res) {
        if (res.status === 404) {
          fetch("/api/learning-path/" + pathId, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Learning-Path-Token": token,
            },
            body: JSON.stringify(data),
          });
        }
      })
      .catch(function () {});
  }

  // Fetch the saved progress object for the current account from the server.
  function pullProgressFromServer(cb) {
    var token = getToken(),
      pathId = getPathId();
    if (!token || !pathId) {
      cb(null);
      return;
    }
    fetch("/api/learning-path/" + pathId, {
      headers: { "X-Learning-Path-Token": token },
    })
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (body) {
        cb(body && body.data ? body.data : null);
      })
      .catch(function () {
        cb(null);
      });
  }

  // ---- patch script.js progress functions ----
  // Override saveProgressState: skip localStorage, only push to server.
  // On page load, pull server progress (if signed in) and apply it; if signed
  // out, wipe any stale localStorage progress so it stays blank.

  window.addEventListener("load", function () {
    if (typeof window.saveProgressState === "function") {
      window.saveProgressState = function () {
        if (isLoggedIn() && window.progress) {
          pushProgressToServer(window.progress);
        }
        // deliberately NOT writing to localStorage — progress is server-only
      };
    }

    if (isLoggedIn()) {
      pullProgressFromServer(applyServerProgress);
    } else {
      try {
        localStorage.removeItem("devpathUserProgress");
      } catch (e) {}
    }

    interceptBookmarks();
  });

  // Merge a progress object pulled from the server into window.progress
  // and refresh the on-page widgets that depend on it.
  //
  // This must be a non-destructive merge: script.js may have already
  // recorded an action (view, search, code open, completion) on this very
  // page load, before this pull finished and before saveProgressState was
  // overridden below. A naive overwrite would stomp that fresh progress
  // with the older server copy. Instead we OR badges, union arrays, and
  // take the max of counters, then push the corrected result back up.
  function applyServerProgress(serverData) {
    if (!serverData || !window.progress) return;
    var p = window.progress;

    function unionArrays(a, b, keyFn) {
      var seen = {};
      var out = [];
      (a || []).concat(b || []).forEach(function (item) {
        var k = keyFn ? keyFn(item) : item;
        if (!seen[k]) {
          seen[k] = true;
          out.push(item);
        }
      });
      return out;
    }

    if (Array.isArray(serverData.viewedProjects)) {
      p.viewedProjects = unionArrays(
        p.viewedProjects,
        serverData.viewedProjects,
      );
      p.projectViews = p.viewedProjects.length;
    }
    if (Array.isArray(serverData.completedProjects)) {
      p.completedProjects = unionArrays(
        p.completedProjects,
        serverData.completedProjects,
        function (item) {
          return item && item.id ? item.id : item;
        },
      );
      p.completions = p.completedProjects.length;
    }
    if (Array.isArray(serverData.achievements)) {
      p.achievements = unionArrays(
        p.achievements,
        serverData.achievements,
        function (item) {
          return item.title;
        },
      ).slice(0, 5);
    }

    // Badges: a badge earned either locally or on the server stays earned.
    if (serverData.badges) {
      p.badges = p.badges || {};
      Object.keys(serverData.badges).forEach(function (key) {
        p.badges[key] = !!p.badges[key] || !!serverData.badges[key];
      });
    }

    // searches/codeOpens don't have arrays to union from, so take the max
    // of local (this page's session) vs server (other sessions/devices).
    ["searches", "codeOpens"].forEach(function (key) {
      if (typeof serverData[key] === "number") {
        p[key] = Math.max(p[key] || 0, serverData[key]);
      }
    });

    if (typeof window.computeProgressPoints === "function")
      window.computeProgressPoints();
    if (typeof window.updateProfileWidgets === "function")
      window.updateProfileWidgets();

    // Push the corrected, merged state back to the server immediately so
    // this page's freshly-earned progress is never silently lost.
    if (typeof window.saveProgressState === "function")
      window.saveProgressState();
  }

  // ---- block saves + badges when signed out ----

  // Open the sign-in modal and surface a hint explaining why.
  function showSignInPrompt(msg) {
    openModal();
    var errorEl = document.getElementById("auth-error");
    if (errorEl) {
      errorEl.textContent = msg || "Please sign in first.";
      errorEl.style.display = "block";
    }
  }

  // Wrap DevPathBookmarks.save/toggle so saving a project (and therefore
  // earning the related badges) requires being signed in.
  function interceptBookmarks() {
    if (!window.DevPathBookmarks) return;
    var origSave = window.DevPathBookmarks.save;
    var origToggle = window.DevPathBookmarks.toggle;

    window.DevPathBookmarks.save = function (project) {
      if (!isLoggedIn()) {
        showSignInPrompt("Sign in to save projects.");
        return false;
      }
      return origSave.call(window.DevPathBookmarks, project);
    };
    window.DevPathBookmarks.toggle = function (project, button) {
      if (!isLoggedIn()) {
        showSignInPrompt("Sign in to save projects.");
        return;
      }
      return origToggle.call(window.DevPathBookmarks, project, button);
    };
  }

  // ---- reset on logout ----

  // Wipe in-memory and stored progress, reset every form field tied to
  // a session (search bar, recommendation form, skill chips, bookmarks).
  function clearAndResetUI() {
    if (window.progress) {
      window.progress.searches = 0;
      window.progress.projectViews = 0;
      window.progress.codeOpens = 0;
      window.progress.completions = 0;
      window.progress.points = 0;
      window.progress.bestScore = 0;
      window.progress.viewedProjects = [];
      window.progress.completedProjects = [];
      window.progress.achievements = [];
      window.progress.badges = {
        first_search: false,
        project_explorer: false,
        code_starter: false,
        completionist: false,
        roadmap_runner: false,
      };
    }
    try {
      localStorage.removeItem("devpathUserProgress");
    } catch (e) {}

    var topicSearch = document.getElementById("topic-search");
    if (topicSearch) topicSearch.value = "";

    ["level", "interest", "time"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.value = "";
    });

    if (typeof window.clearSkills === "function") window.clearSkills();

    if (
      window.DevPathBookmarks &&
      typeof window.DevPathBookmarks.clearSession === "function"
    ) {
      window.DevPathBookmarks.clearSession();
    }

    if (typeof window.computeProgressPoints === "function")
      window.computeProgressPoints();
    if (typeof window.updateProfileWidgets === "function")
      window.updateProfileWidgets();
  }

  // ---- logout ----

  // Invalidate the server session, clear local auth state, and reset the UI.
  function doLogout() {
    fetch("/api/auth/logout", {
      method: "POST",
      headers: { "X-Auth-Token": getToken() },
    }).finally(function () {
      lsDel(AUTH_TOKEN_KEY);
      lsDel(AUTH_USER_KEY);
      lsDel(AUTH_PATH_KEY);
      clearAndResetUI();
      updateNavUI();
      updateSubtitle();
      showToast("Successfully logged out");
    });
  }

  // ---- modal ----

  // Build the sign in / sign up modal once and append it to the document.
  // Styling comes entirely from the .auth-modal-* classes in style.css.
  function injectModal() {
    var el = document.createElement("div");
    el.id = "auth-modal-overlay";
    el.className = "auth-modal-overlay";

    el.innerHTML = [
      '<div class="auth-modal-card">',
      '<div class="auth-modal-header">',
      '<h2 id="auth-modal-title" class="auth-modal-title">Sign In</h2>',
      '<button id="auth-modal-close" type="button" aria-label="Close" class="auth-modal-close">&times;</button>',
      "</div>",

      '<div class="auth-tabs">',
      '<button id="auth-tab-login" type="button" class="auth-tab auth-tab--active">Sign In</button>',
      '<button id="auth-tab-register" type="button" class="auth-tab">Sign Up</button>',
      "</div>",

      '<div id="auth-error" class="auth-error"></div>',

      '<div class="auth-form">',
      '<input id="auth-username" type="text" placeholder="Username" autocomplete="username" class="auth-input">',
      '<input id="auth-password" type="password" placeholder="Password" autocomplete="current-password" class="auth-input">',
      '<button id="auth-submit-btn" type="button" class="auth-submit-btn">Sign In</button>',
      "</div>",
      "</div>",
    ].join("");

    document.body.appendChild(el);
    wireModalEvents(el);
  }

  // Attach all event handlers for the modal (tabs, submit, close, enter-key).
  function wireModalEvents(overlay) {
    var closeBtn = document.getElementById("auth-modal-close");
    var tabLogin = document.getElementById("auth-tab-login");
    var tabReg = document.getElementById("auth-tab-register");
    var submitBtn = document.getElementById("auth-submit-btn");
    var errorEl = document.getElementById("auth-error");
    var titleEl = document.getElementById("auth-modal-title");
    var mode = "login";

    // Switch the modal between login and register mode.
    function setMode(m) {
      mode = m;
      titleEl.textContent = m === "login" ? "Sign In" : "Create Account";
      submitBtn.textContent = m === "login" ? "Sign In" : "Sign Up";
      document
        .getElementById("auth-password")
        .setAttribute(
          "autocomplete",
          m === "login" ? "current-password" : "new-password",
        );
      tabLogin.classList.toggle("auth-tab--active", m === "login");
      tabReg.classList.toggle("auth-tab--active", m === "register");
      showError("");
    }

    // Show or clear the inline error banner.
    function showError(msg) {
      errorEl.textContent = msg;
      errorEl.style.display = msg ? "block" : "none";
    }

    tabLogin.addEventListener("click", function () {
      setMode("login");
    });
    tabReg.addEventListener("click", function () {
      setMode("register");
    });
    closeBtn.addEventListener("click", closeModal);
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeModal();
    });

    // Submit the form to /api/auth/login or /api/auth/register depending on mode.
    submitBtn.addEventListener("click", function () {
      var username = document.getElementById("auth-username").value.trim();
      var password = document.getElementById("auth-password").value.trim();
      if (!username || !password) {
        showError("Fill in both fields.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "...";

      fetch(mode === "login" ? "/api/auth/login" : "/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username, password: password }),
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          submitBtn.disabled = false;
          submitBtn.textContent = mode === "login" ? "Sign In" : "Sign Up";
          if (!result.ok) {
            var msg = result.data.error || "Something went wrong.";
            if (
              mode === "login" &&
              msg.toLowerCase().indexOf("invalid") !== -1
            ) {
              msg =
                "Invalid username or password. No account yet? Switch to Sign Up.";
            }
            showError(msg);
            return;
          }
          lsSet(AUTH_TOKEN_KEY, result.data.token);
          lsSet(AUTH_USER_KEY, result.data.username);
          lsSet(AUTH_PATH_KEY, result.data.path_id);
          closeModal();
          updateNavUI();
          updateSubtitle();
          showToast(
            mode === "login"
              ? "Successfully signed in"
              : "Successfully signed up",
          );
          pullProgressFromServer(applyServerProgress);
        })
        .catch(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = mode === "login" ? "Sign In" : "Sign Up";
          showError("Network error. Try again.");
        });
    });

    ["auth-username", "auth-password"].forEach(function (id) {
      document.getElementById(id).addEventListener("keydown", function (e) {
        if (e.key === "Enter") submitBtn.click();
      });
    });
  }

  // Show the sign in / sign up modal.
  function openModal() {
    var o = document.getElementById("auth-modal-overlay");
    if (o) o.style.display = "flex";
  }
  // Hide the sign in / sign up modal.
  function closeModal() {
    var o = document.getElementById("auth-modal-overlay");
    if (o) o.style.display = "none";
  }

  // ---- dashboard ----

  // Build the slide-in dashboard panel once and append it to the document.
  // Styling comes entirely from the .auth-dashboard-* classes in style.css.
  function injectDashboard() {
    var el = document.createElement("div");
    el.id = "auth-dashboard";
    el.className = "auth-dashboard";

    el.innerHTML = [
      '<div class="auth-dashboard-header">',
      "<div>",
      '<div class="auth-dashboard-label">Dashboard</div>',
      '<div id="dash-username" class="auth-dashboard-username"></div>',
      "</div>",
      '<button id="dash-close" type="button" aria-label="Close" class="auth-dashboard-close">&times;</button>',
      "</div>",

      '<div class="auth-dashboard-body">',

      '<div class="auth-points-card">',
      '<div class="auth-points-row">',
      '<span class="auth-points-label">Points</span>',
      '<span id="dash-points" class="auth-points-value">0</span>',
      "</div>",
      '<div class="auth-meter-track"><div id="dash-meter" class="auth-meter-fill"></div></div>',
      "</div>",

      '<div class="auth-stats-grid">',
      '<div class="auth-stat-card"><div id="dash-stat-searches" class="auth-stat-value">0</div><div class="auth-stat-label">Searches</div></div>',
      '<div class="auth-stat-card"><div id="dash-stat-viewed" class="auth-stat-value">0</div><div class="auth-stat-label">Viewed</div></div>',
      '<div class="auth-stat-card"><div id="dash-stat-codeopens" class="auth-stat-value">0</div><div class="auth-stat-label">Code Opens</div></div>',
      '<div class="auth-stat-card"><div id="dash-stat-completed" class="auth-stat-value">0</div><div class="auth-stat-label">Completed</div></div>',
      "</div>",

      '<div class="auth-section">',
      '<div class="auth-section-label">Badges</div>',
      '<div id="dash-badges" class="auth-badges-list"></div>',
      "</div>",

      '<div class="auth-section">',
      '<div class="auth-section-label">Saved Projects</div>',
      '<div id="dash-saved" class="auth-saved-list auth-saved-list--cards"></div>',
      "</div>",

      '<div class="auth-section-label">Quick Links</div>',
      '<div class="auth-quick-links">',
      '<a href="#find-project" onclick="window.closeDashboard()" class="auth-quick-link">&#x2192; Find a Project</a>',
      '<a href="#progress" onclick="window.closeDashboard()" class="auth-quick-link">&#x2192; Progress &amp; Badges</a>',
      "</div>",

      "</div>",

      '<div class="auth-dashboard-footer">',
      '<button id="dash-logout" type="button" class="auth-logout-action-btn">Log Out</button>',
      "</div>",
    ].join("");

    document.body.appendChild(el);
    document
      .getElementById("dash-close")
      .addEventListener("click", closeDashboard);
    document
      .getElementById("dash-logout")
      .addEventListener("click", function () {
        closeDashboard();
        doLogout();
      });
  }

  // Slide the dashboard panel into view and refresh its contents.
  function openDashboard() {
    var dash = document.getElementById("auth-dashboard");
    if (!dash) return;
    refreshDashboard();
    dash.classList.add("auth-dashboard--open");
  }

  // Slide the dashboard panel out of view.
  function closeDashboard() {
    var dash = document.getElementById("auth-dashboard");
    if (dash) dash.classList.remove("auth-dashboard--open");
  }

  // Exposed globally so the inline onclick on dashboard quick-links can call it.
  window.closeDashboard = closeDashboard;

  // Return the CSS class for a level tag based on its value.
  function levelTagClass(level) {
    if (level === "Beginner") return "auth-tag auth-tag--level-beginner";
    if (level === "Intermediate")
      return "auth-tag auth-tag--level-intermediate";
    if (level === "Advanced") return "auth-tag auth-tag--level-advanced";
    return "auth-tag";
  }

  // Repaint every widget in the dashboard from the current window.progress
  // and DevPathBookmarks state. Called each time the dashboard is opened.
  function refreshDashboard() {
    var p = window.progress;
    if (!p) return;

    var u = document.getElementById("dash-username");
    if (u) u.textContent = getUser() || "";
    var pt = document.getElementById("dash-points");
    if (pt) pt.textContent = p.points || 0;
    var m = document.getElementById("dash-meter");
    if (m) {
      var pct = Math.min(
        100,
        Math.round(
          ((p.points || 0) / (window.PROGRESS_MAX_POINTS || 500)) * 100,
        ),
      );
      m.style.width = pct + "%";
    }
    var s = document.getElementById("dash-stat-searches");
    if (s) s.textContent = p.searches || 0;
    var v = document.getElementById("dash-stat-viewed");
    if (v) v.textContent = p.projectViews || 0;
    var co = document.getElementById("dash-stat-codeopens");
    if (co) co.textContent = p.codeOpens || 0;
    var cp = document.getElementById("dash-stat-completed");
    if (cp) cp.textContent = p.completions || 0;

    renderDashboardBadges(p.badges || {});
    renderDashboardSaved();
  }

  // Render the badge unlock list inside the dashboard.
  function renderDashboardBadges(badges) {
    var badgesEl = document.getElementById("dash-badges");
    if (!badgesEl) return;
    var defs = [
      ["first_search", "First Search"],
      ["project_explorer", "Project Explorer"],
      ["code_starter", "Code Starter"],
      ["completionist", "Completionist"],
      ["roadmap_runner", "Roadmap Runner"],
    ];
    badgesEl.innerHTML = defs
      .map(function (b) {
        var unlocked = !!badges[b[0]];
        return (
          '<div class="auth-badge-row' +
          (unlocked ? " auth-badge-row--unlocked" : "") +
          '">' +
          "<span>" +
          (unlocked ? "✅" : "🔒") +
          "</span>" +
          '<span class="auth-badge-name' +
          (unlocked ? " auth-badge-name--unlocked" : "") +
          '">' +
          b[1] +
          "</span>" +
          "</div>"
        );
      })
      .join("");
  }

  // Render the saved-projects list inside the dashboard as mini project cards
  // matching the colours and layout of the main .project-card component.
  function renderDashboardSaved() {
    var savedEl = document.getElementById("dash-saved");
    if (!savedEl) return;
    var saved = window.DevPathBookmarks
      ? window.DevPathBookmarks.getSaved()
      : [];

    if (!saved.length) {
      savedEl.innerHTML =
        '<span class="auth-saved-empty">No saved projects yet.</span>';
      return;
    }

    savedEl.innerHTML = saved
      .slice(0, 5)
      .map(function (proj) {
        var tags = (Array.isArray(proj.skills) ? proj.skills.slice(0, 3) : [])
          .map(function (skill) {
            return '<span class="auth-tag">' + skill + "</span>";
          })
          .join("");
        if (proj.level)
          tags +=
            '<span class="' +
            levelTagClass(proj.level) +
            '">' +
            proj.level +
            "</span>";
        if (proj.time)
          tags +=
            '<span class="auth-tag auth-tag--time">' + proj.time + "</span>";

        return (
          '<a href="/project/' +
          proj.id +
          '" onclick="window.closeDashboard()" class="auth-saved-card-link">' +
          '<div class="auth-saved-card">' +
          '<span class="auth-saved-card-title">' +
          proj.title +
          "</span>" +
          (tags ? '<div class="auth-saved-card-tags">' + tags + "</div>" : "") +
          "</div>" +
          "</a>"
        );
      })
      .join("");
  }

  // ---- nav UI ----

  // Show/hide the Sign In button and Dashboard button in the navbar
  // based on current sign-in state.
  // ---- nav UI ----

  // Show/hide the Sign In button and Dashboard button in both the desktop
  // navbar and the mobile menu based on current sign-in state.
  function updateNavUI() {
    var signInBtn = document.getElementById("auth-nav-btn");
    var dashBtn = document.getElementById("auth-logout-btn");
    var signInBtnMobile = document.getElementById("auth-nav-btn-mobile");
    var dashBtnMobile = document.getElementById("auth-logout-btn-mobile");
    if (!signInBtn) return;

    var loggedIn = isLoggedIn();
    signInBtn.classList.toggle("auth-hidden", loggedIn);
    if (dashBtn) dashBtn.classList.toggle("auth-hidden", !loggedIn);
    if (signInBtnMobile)
      signInBtnMobile.classList.toggle("auth-hidden", loggedIn);
    if (dashBtnMobile) dashBtnMobile.classList.toggle("auth-hidden", !loggedIn);
  }

  // Update the progress section subtitle to reflect sign-in state.
  function updateSubtitle() {
    var sub = document.getElementById("progress-section-sub");
    if (!sub) return;
    sub.textContent = isLoggedIn()
      ? "Signed in as " + getUser() + " — progress syncs to the server."
      : "Sign in to track and sync your progress across devices.";
  }

  // ---- init ----

  document.addEventListener("DOMContentLoaded", function () {
    injectModal();
    injectDashboard();
    injectToast();
    updateNavUI();
    updateSubtitle();

    // Desktop buttons
    var signInBtn = document.getElementById("auth-nav-btn");
    if (signInBtn) signInBtn.onclick = openModal;

    var dashBtn = document.getElementById("auth-logout-btn");
    if (dashBtn) dashBtn.onclick = openDashboard;

    // Mobile menu buttons — same actions as desktop
    var signInBtnMobile = document.getElementById("auth-nav-btn-mobile");
    if (signInBtnMobile) signInBtnMobile.onclick = openModal;

    var dashBtnMobile = document.getElementById("auth-logout-btn-mobile");
    if (dashBtnMobile) dashBtnMobile.onclick = openDashboard;
  });
})();
