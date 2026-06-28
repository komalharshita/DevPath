// Progress tracking dashboard with visual charts
// Displays learner progress metrics and activity streaks

(function() {
  'use strict';

  var ProgressDashboard = {
    /**
     * Initialize progress dashboard
     */
    init: function(userId, progressData) {
      ProgressDashboard.renderProgressRing(
        progressData.completionPercentage
      );
      ProgressDashboard.renderActivityChart(progressData.weeklyActivity);
      ProgressDashboard.renderStreakCounter(progressData.streakDays);
      ProgressDashboard.renderPathProgress(progressData.paths);
    },

    /**
     * Render circular progress ring using CSS
     */
    renderProgressRing: function(percentage) {
      var container = document.getElementById('progress-ring');

      if (!container) return;

      var svg = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'svg'
      );
      svg.setAttribute('width', '150');
      svg.setAttribute('height', '150');
      svg.setAttribute('viewBox', '0 0 150 150');

      // Background circle
      var bgCircle = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'circle'
      );
      bgCircle.setAttribute('cx', '75');
      bgCircle.setAttribute('cy', '75');
      bgCircle.setAttribute('r', '65');
      bgCircle.setAttribute('fill', 'none');
      bgCircle.setAttribute('stroke', '#e0e0e0');
      bgCircle.setAttribute('stroke-width', '8');

      // Progress circle
      var progressCircle = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'circle'
      );
      progressCircle.setAttribute('cx', '75');
      progressCircle.setAttribute('cy', '75');
      progressCircle.setAttribute('r', '65');
      progressCircle.setAttribute('fill', 'none');
      progressCircle.setAttribute('stroke', '#4CAF50');
      progressCircle.setAttribute('stroke-width', '8');
      progressCircle.setAttribute('stroke-dasharray', 408);
      progressCircle.setAttribute(
        'stroke-dashoffset',
        408 - (percentage / 100) * 408
      );
      progressCircle.setAttribute(
        'style',
        'transition: stroke-dashoffset 0.5s ease; transform-origin: 75px 75px; transform: rotate(-90deg)'
      );

      // Percentage text
      var text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', '75');
      text.setAttribute('y', '75');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dy', '.3em');
      text.setAttribute('font-size', '32');
      text.setAttribute('font-weight', 'bold');
      text.setAttribute('fill', '#333');
      text.textContent = percentage + '%';

      svg.appendChild(bgCircle);
      svg.appendChild(progressCircle);
      svg.appendChild(text);
      container.appendChild(svg);
    },

    /**
     * Render weekly activity bar chart
     */
    renderActivityChart: function(weeklyData) {
      var container = document.getElementById('activity-chart');

      if (!container || !weeklyData || weeklyData.length === 0) return;

      var maxValue = Math.max.apply(null, weeklyData);
      var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

      var html = '<div class="chart-container">';

      for (var i = 0; i < weeklyData.length; i++) {
        var value = weeklyData[i];
        var percentage = (value / maxValue) * 100;
        var day = days[i];

        html +=
          '<div class="chart-bar-wrapper">' +
          '<div class="chart-bar" style="height: ' +
          percentage +
          '%;" title="' +
          value +
          ' activities"></div>' +
          '<div class="chart-label">' +
          day +
          '</div>' +
          '</div>';
      }

      html += '</div>';
      container.innerHTML = html;

      // Add styles
      var style = document.createElement('style');
      style.textContent = `
        .chart-container {
          display: flex;
          align-items: flex-end;
          justify-content: space-around;
          height: 200px;
          gap: 10px;
          padding: 10px;
          background: #f9f9f9;
          border-radius: 8px;
        }
        .chart-bar-wrapper {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
        }
        .chart-bar {
          width: 100%;
          background: linear-gradient(180deg, #4CAF50, #45a049);
          border-radius: 4px 4px 0 0;
          transition: background 0.3s ease;
          min-height: 4px;
        }
        .chart-bar:hover {
          background: linear-gradient(180deg, #45a049, #3d8b40);
        }
        .chart-label {
          font-size: 12px;
          color: #666;
          font-weight: 500;
        }
      `;

      if (!document.getElementById('progress-chart-styles')) {
        style.id = 'progress-chart-styles';
        document.head.appendChild(style);
      }
    },

    /**
     * Render streak counter
     */
    renderStreakCounter: function(streakDays) {
      var container = document.getElementById('streak-counter');

      if (!container) return;

      var html =
        '<div class="streak-badge">' +
        '<span class="streak-flame">🔥</span>' +
        '<span class="streak-number">' +
        streakDays +
        '</span>' +
        '<span class="streak-label">day streak</span>' +
        '</div>';

      container.innerHTML = html;

      // Add styles
      var style = document.createElement('style');
      style.textContent = `
        .streak-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          background: linear-gradient(135deg, #FF6B35, #FF8C42);
          color: white;
          padding: 12px 20px;
          border-radius: 25px;
          font-weight: bold;
          width: fit-content;
          box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }
        .streak-flame {
          font-size: 24px;
        }
        .streak-number {
          font-size: 18px;
        }
        .streak-label {
          font-size: 12px;
          opacity: 0.9;
        }
      `;

      if (!document.getElementById('progress-streak-styles')) {
        style.id = 'progress-streak-styles';
        document.head.appendChild(style);
      }
    },

    /**
     * Render individual path progress
     */
    renderPathProgress: function(paths) {
      var container = document.getElementById('path-progress-list');

      if (!container || !paths) return;

      var html = '';

      for (var i = 0; i < paths.length; i++) {
        var path = paths[i];
        var percentage = path.completed / path.total * 100;

        html +=
          '<div class="path-progress-item">' +
          '<div class="path-header">' +
          '<h4>' +
          path.name +
          '</h4>' +
          '<span class="path-percentage">' +
          Math.round(percentage) +
          '%</span>' +
          '</div>' +
          '<div class="progress-bar">' +
          '<div class="progress-fill" style="width: ' +
          percentage +
          '%"></div>' +
          '</div>' +
          '<div class="path-meta">' +
          '<span>' +
          path.completed +
          ' of ' +
          path.total +
          ' topics</span>' +
          '</div>' +
          '</div>';
      }

      container.innerHTML = html;

      // Add styles
      var style = document.createElement('style');
      style.textContent = `
        .path-progress-item {
          margin-bottom: 20px;
          padding: 15px;
          background: white;
          border-radius: 8px;
          border-left: 4px solid #4CAF50;
        }
        .path-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }
        .path-header h4 {
          margin: 0;
          color: #333;
        }
        .path-percentage {
          font-weight: bold;
          color: #4CAF50;
          font-size: 14px;
        }
        .progress-bar {
          height: 8px;
          background: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 8px;
        }
        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #4CAF50, #45a049);
          transition: width 0.3s ease;
        }
        .path-meta {
          font-size: 12px;
          color: #999;
        }
      `;

      if (!document.getElementById('progress-path-styles')) {
        style.id = 'progress-path-styles';
        document.head.appendChild(style);
      }
    }
  };

  // Export for external use
  window.ProgressDashboard = ProgressDashboard;
})();
