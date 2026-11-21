(function () {
  var projectId = window.PROJECT_ID;
  var isSignedIn = window.USER_LOGGED_IN === true;
  var checkboxes = Array.prototype.slice.call(document.querySelectorAll(".roadmap-checkbox"));
  var progressFill = document.getElementById("roadmap-progress-fill");
  var progressText = document.getElementById("roadmap-progress-text");
  var progressBar = document.querySelector(".roadmap-progress-bar");
  var completionContainer = document.getElementById("completion-container");
  var completionButton = document.getElementById("btn-complete-project");
  var completionMessage = document.getElementById("completion-message");
  var stepsKey = "devpath-roadmap-progress-" + projectId;
  var isCompleted = typeof projectIsCompleted === "function" && projectIsCompleted(projectId);

  if (!projectId || !checkboxes.length) return;

  function readLocalSteps() {
    try {
      var saved = JSON.parse(localStorage.getItem(stepsKey) || "[]");
      return Array.isArray(saved) ? saved : [];
    } catch (error) {
      return [];
    }
  }

  function writeLocalSteps() {
    try {
      localStorage.setItem(stepsKey, JSON.stringify(checkboxes.map(function (checkbox) {
        return checkbox.checked;
      })));
    } catch (error) {
      return;
    }
  }

  function renderProgress(save) {
    var completedCount = checkboxes.filter(function (checkbox) {
      return checkbox.checked;
    }).length;
    var percentage = Math.round((completedCount / checkboxes.length) * 100);
    var allStepsDone = completedCount === checkboxes.length;
    if (!allStepsDone) isCompleted = false;
    var markedComplete = allStepsDone && isCompleted;

    checkboxes.forEach(function (checkbox) {
      var step = checkbox.closest(".roadmap-step");
      if (step) step.classList.toggle("completed", checkbox.checked);
    });

    if (progressFill) progressFill.style.width = percentage + "%";
    if (progressText) progressText.textContent = percentage + "% completed";
    if (progressBar) progressBar.setAttribute("aria-valuenow", String(percentage));
    if (completionContainer) completionContainer.hidden = !allStepsDone || markedComplete;
    if (completionButton) {
      completionButton.disabled = !allStepsDone || markedComplete;
      completionButton.textContent = markedComplete ? "Project Completed" : "Mark Project Complete";
    }
    if (completionMessage) completionMessage.hidden = !markedComplete;

    if (!save) return;

    writeLocalSteps();
    if (isSignedIn) {
      fetch("/api/project/" + projectId + "/progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed_steps: checkboxes.map(function (checkbox) {
          return checkbox.checked;
        }) })
      }).catch(function () {});
    }
  }

  function restoreSteps(completedSteps) {
    checkboxes.forEach(function (checkbox, index) {
      checkbox.checked = completedSteps[index] === true;
    });
    renderProgress(false);
  }

  checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      renderProgress(true);
    });
  });

  if (completionButton) {
    completionButton.addEventListener("click", function () {
      if (!checkboxes.every(function (checkbox) { return checkbox.checked; })) return;
      isCompleted = true;
      renderProgress(false);
    });
  }

  if (isSignedIn) {
    fetch("/api/project/" + projectId + "/progress")
      .then(function (response) {
        if (!response.ok) throw new Error("Roadmap progress unavailable");
        return response.json();
      })
      .then(function (data) { restoreSteps(data.completed_steps || []); })
      .catch(function () { restoreSteps(readLocalSteps()); });
  } else {
    restoreSteps(readLocalSteps());
  }
})();
