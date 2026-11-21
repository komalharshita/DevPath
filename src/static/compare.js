// compare.js — Career roadmap comparison page logic

(function () {
  var selectA = document.getElementById("roadmap-select-a");
  var selectB = document.getElementById("roadmap-select-b");
  var compareBtn = document.getElementById("compare-btn");
  var errorEl = document.getElementById("compare-error");
  var emptyEl = document.getElementById("compare-empty");
  var resultsEl = document.getElementById("compare-results");
  var quickBtns = document.querySelectorAll(".compare-quick-btn");

  if (!selectA || !selectB || !compareBtn) return;

  function showError(message) {
    if (!errorEl) return;
    errorEl.textContent = message;
    errorEl.hidden = !message;
    errorEl.classList.toggle("hidden", !message);
  }

  function setLoading(isLoading) {
    compareBtn.disabled = isLoading;
    compareBtn.textContent = isLoading ? "Comparing…" : "Compare Roadmaps";
  }

  function renderBarChart(container, labelA, labelB, valueA, valueB, maxValue, unit) {
    if (!container) return;
    container.innerHTML = "";

    var rows = [
      { label: labelA, value: valueA, cls: "compare-bar--a" },
      { label: labelB, value: valueB, cls: "compare-bar--b" },
    ];

    rows.forEach(function (row) {
      var pct = maxValue > 0 ? Math.round((row.value / maxValue) * 100) : 0;
      var wrap = document.createElement("div");
      wrap.className = "compare-bar-row";

      var name = document.createElement("span");
      name.className = "compare-bar-label";
      name.textContent = row.label;

      var track = document.createElement("div");
      track.className = "compare-bar-track";
      track.setAttribute("role", "meter");
      track.setAttribute("aria-valuemin", "0");
      track.setAttribute("aria-valuemax", String(maxValue));
      track.setAttribute("aria-valuenow", String(row.value));
      track.setAttribute("aria-label", row.label + " metric: " + row.value + (unit || ""));

      var fill = document.createElement("div");
      fill.className = "compare-bar-fill " + row.cls;
      fill.style.width = pct + "%";

      var val = document.createElement("span");
      val.className = "compare-bar-value";
      val.textContent = row.value + (unit || "");

      track.appendChild(fill);
      wrap.appendChild(name);
      wrap.appendChild(track);
      wrap.appendChild(val);
      container.appendChild(wrap);
    });
  }

  function renderTagList(el, items, sharedSet, side) {
    if (!el) return;
    el.innerHTML = "";
    items.forEach(function (item) {
      var li = document.createElement("li");
      li.textContent = item;
      var norm = item.toLowerCase();
      var isShared = sharedSet && sharedSet.has(norm);
      li.className = isShared ? "compare-tag compare-tag--shared" : "compare-tag compare-tag--" + side;
      li.textContent = isShared ? item + " (shared)" : item;
      el.appendChild(li);
    });
  }

  function renderComparison(data) {
    var a = data.roadmap_a;
    var b = data.roadmap_b;
    var metrics = data.metrics;

    document.getElementById("summary-title-a").textContent = a.title;
    document.getElementById("summary-desc-a").textContent = a.description;
    document.getElementById("summary-title-b").textContent = b.title;
    document.getElementById("summary-desc-b").textContent = b.description;

    document.getElementById("shared-skills-count").textContent = data.summary.shared_skills_count;
    document.getElementById("shared-topics-count").textContent = data.summary.shared_topics_count;

    document.getElementById("detail-title-a").textContent = a.title;
    document.getElementById("detail-title-b").textContent = b.title;
    document.getElementById("meta-duration-a").textContent = a.duration;
    document.getElementById("meta-duration-b").textContent = b.duration;
    document.getElementById("meta-difficulty-a").textContent = a.difficulty;
    document.getElementById("meta-difficulty-b").textContent = b.difficulty;

    var sharedTopicSet = new Set(
      data.overlapping_topics.map(function (t) { return t.toLowerCase(); })
    );

    renderTagList(document.getElementById("topics-a"), a.topics, sharedTopicSet, "a");
    renderTagList(document.getElementById("topics-b"), b.topics, sharedTopicSet, "b");
    renderTagList(document.getElementById("roles-a"), a.career_opportunities, null, "a");
    renderTagList(document.getElementById("roles-b"), b.career_opportunities, null, "b");
    renderTagList(document.getElementById("skills-a"), a.skills, new Set(data.overlapping_skills.map(function (skill) { return skill.toLowerCase(); })), "a");
    renderTagList(document.getElementById("skills-b"), b.skills, new Set(data.overlapping_skills.map(function (skill) { return skill.toLowerCase(); })), "b");

    var maxTopics = Math.max(metrics.topics_count.a, metrics.topics_count.b, 1);
    var maxSkills = Math.max(metrics.skills_count.a, metrics.skills_count.b, 1);

    renderBarChart(
      document.getElementById("chart-duration"),
      a.title, b.title,
      metrics.duration_weeks.a, metrics.duration_weeks.b,
      metrics.duration_weeks.max, " wks"
    );
    renderBarChart(
      document.getElementById("chart-difficulty"),
      a.title, b.title,
      metrics.difficulty_score.a, metrics.difficulty_score.b,
      metrics.difficulty_score.max, "/5"
    );
    renderBarChart(
      document.getElementById("chart-topics"),
      a.title, b.title,
      metrics.topics_count.a, metrics.topics_count.b,
      maxTopics, ""
    );
    renderBarChart(
      document.getElementById("chart-skills"),
      a.title, b.title,
      metrics.skills_count.a, metrics.skills_count.b,
      maxSkills, ""
    );

    emptyEl.hidden = true;
    emptyEl.classList.add("hidden");
    resultsEl.hidden = false;
    resultsEl.classList.remove("hidden");
    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function runComparison() {
    var idA = selectA.value;
    var idB = selectB.value;

    showError("");

    if (!idA || !idB) {
      showError("Please select both roadmaps before comparing.");
      return;
    }

    if (idA === idB) {
      showError("Please select two different roadmaps to compare.");
      return;
    }

    setLoading(true);

    fetch("/api/compare?a=" + encodeURIComponent(idA) + "&b=" + encodeURIComponent(idB))
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, status: res.status, body: body };
        });
      })
      .then(function (result) {
        if (!result.ok) {
          showError(result.body.error || "Comparison failed. Please try again.");
          return;
        }
        renderComparison(result.body);
      })
      .catch(function () {
        showError("Network error. Please check your connection and try again.");
      })
      .finally(function () {
        setLoading(false);
      });
  }

  compareBtn.addEventListener("click", runComparison);

  quickBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      selectA.value = btn.getAttribute("data-a") || "";
      selectB.value = btn.getAttribute("data-b") || "";
      runComparison();
    });
  });

  // Pre-select from URL query params: /compare?a=frontend&b=fullstack
  var params = new URLSearchParams(window.location.search);
  var paramA = params.get("a");
  var paramB = params.get("b");
  if (paramA) selectA.value = paramA;
  if (paramB) selectB.value = paramB;
  if (paramA && paramB) runComparison();
})();
