/**
 * static/recently-viewed.js
 * Recently Viewed Projects tracking utility for DevPath.
 *
 * Responsibilities
 * ----------------
 * 1. Track project views - record when users click on or visit projects
 * 2. Persist data - store in localStorage across browser sessions
 * 3. Deduplication - if same project viewed again, move to top, don't duplicate
 * 4. Render panel - display up to 5 most recent projects
 * 5. Clear history - remove all tracked projects
 *
 * Public API
 * ----------
 * RecentlyViewed.trackView(project)    – track a project view
 * RecentlyViewed.getRecentlyViewed()   – get array of all tracked projects
 * RecentlyViewed.isTracked(id)         – boolean check if project is tracked
 * RecentlyViewed.clearHistory()        – remove all tracked projects
 * RecentlyViewed.renderPanel()         – redraw the recently viewed panel
 */

var RecentlyViewed = (function () {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* Constants                                                            */
  /* ------------------------------------------------------------------ */
  var STORAGE_KEY = "devpathRecentlyViewed";
  var MAX_ITEMS = 10;           // Store max 10 items in localStorage
  var DISPLAY_ITEMS = 5;        // Display max 5 in UI
  var PANEL_ID = "recently-viewed-panel";
  var LIST_ID = "recently-viewed-list";

  /* ------------------------------------------------------------------ */
  /* Safe localStorage helpers                                            */
  /* ------------------------------------------------------------------ */
  function lsGet(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch (err) {
      console.warn("[RecentlyViewed] localStorage read error:", err);
      return null;
    }
  }

  function lsSet(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (err) {
      console.warn("[RecentlyViewed] localStorage write error:", err);
      return false;
    }
  }

  /* ------------------------------------------------------------------ */
  /* Time formatting utilities                                            */
  /* ------------------------------------------------------------------ */
  function formatTimeAgo(timestamp) {
    if (!timestamp) return "Recently viewed";

    var now = Date.now();
    var diff = now - timestamp;
    var seconds = Math.floor(diff / 1000);
    var minutes = Math.floor(seconds / 60);
    var hours = Math.floor(minutes / 60);
    var days = Math.floor(hours / 24);

    if (seconds < 60) return "Just now";
    if (minutes < 60) return minutes + " min ago";
    if (hours < 24) return hours + " hour" + (hours > 1 ? "s" : "") + " ago";
    if (days === 1) return "Yesterday";
    if (days < 7) return days + " days ago";
    if (days < 30) return Math.floor(days / 7) + " weeks ago";

    // Format as date for older items
    var date = new Date(timestamp);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }

  /* ------------------------------------------------------------------ */
  /* Recently Viewed Data Management                                      */
  /* ------------------------------------------------------------------ */
  function getRecentlyViewed() {
    var data = lsGet(STORAGE_KEY);
    return Array.isArray(data) ? data : [];
  }

  function isTracked(projectId) {
    return getRecentlyViewed().some(function (p) {
      return String(p.id) === String(projectId);
    });
  }

  function trackView(project) {
    if (!project || !project.id) return false;

    var projectId = project.id;
    var viewed = getRecentlyViewed();

    // Check if already tracked - if so, remove old entry and re-add at top
    viewed = viewed.filter(function (p) {
      return String(p.id) !== String(projectId);
    });

    // Add to top with current timestamp
    var newEntry = {
      id: projectId,
      title: project.title || "Project " + projectId,
      interest: project.interest || "General",
      timestamp: Date.now()
    };

    viewed.unshift(newEntry);

    // Keep only the last MAX_ITEMS
    if (viewed.length > MAX_ITEMS) {
      viewed = viewed.slice(0, MAX_ITEMS);
    }

    lsSet(STORAGE_KEY, viewed);
    renderPanel();
    return true;
  }

  function clearHistory() {
    lsSet(STORAGE_KEY, []);
    renderPanel();
    return true;
  }

  /* ------------------------------------------------------------------ */
  /* Rendering                                                            */
  /* ------------------------------------------------------------------ */
  function renderPanel() {
    var panel = document.getElementById(PANEL_ID);
    if (!panel) return;

    var viewed = getRecentlyViewed();
    var list = document.getElementById(LIST_ID);

    if (!list) return;

    // Clear the list
    list.innerHTML = "";

    // If no recently viewed projects, hide the panel or show empty state
    if (viewed.length === 0) {
      panel.style.display = "none";
      return;
    }

    panel.style.display = "block";

    // Show only the first DISPLAY_ITEMS
    var displayItems = viewed.slice(0, DISPLAY_ITEMS);

    displayItems.forEach(function (project) {
      var card = buildProjectCard(project);
      list.appendChild(card);
    });
  }

  function buildProjectCard(project) {
    var card = document.createElement("div");
    card.className = "recently-viewed-card";
    card.setAttribute("data-project-id", project.id);

    var link = document.createElement("a");
    link.href = "/project/" + project.id;
    link.className = "recently-viewed-link";

    var title = document.createElement("div");
    title.className = "recently-viewed-title";
    title.textContent = project.title;

    var meta = document.createElement("div");
    meta.className = "recently-viewed-meta";

    var interest = document.createElement("span");
    interest.className = "recently-viewed-interest";
    interest.textContent = project.interest;

    var time = document.createElement("span");
    time.className = "recently-viewed-time";
    time.textContent = formatTimeAgo(project.timestamp);

    meta.appendChild(interest);
    meta.appendChild(time);

    link.appendChild(title);
    link.appendChild(meta);

    card.appendChild(link);
    return card;
  }

  /* ------------------------------------------------------------------ */
  /* Public API                                                            */
  /* ------------------------------------------------------------------ */
  return {
    trackView: trackView,
    getRecentlyViewed: getRecentlyViewed,
    isTracked: isTracked,
    clearHistory: clearHistory,
    renderPanel: renderPanel
  };
})();

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function () {
  RecentlyViewed.renderPanel();
});