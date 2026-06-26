import re

with open("src/templates/explore.html", "r") as f:
    content = f.read()

# Replace the hero section, stats section, etc. with a simple explore layout.
# We will find the <main> tag or <header class="hero"> and remove everything until <footer class="footer">
start_tag = '<header class="hero">'
end_tag = '<!-- ============================================================\n       Footer'

start_idx = content.find(start_tag)
end_idx = content.find(end_tag)

if start_idx != -1 and end_idx != -1:
    new_body = """
  <main class="container" style="padding-top: 120px; padding-bottom: 60px; min-height: 80vh;">
    <h1 style="margin-bottom: 1rem;">Explore All Projects</h1>
    <p style="color: var(--text-muted); margin-bottom: 2rem;">Browse our entire catalog of projects, filter by difficulty or interest, and find your next coding challenge.</p>
    
    <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
      <!-- Sidebar Filters -->
      <aside style="flex: 1; min-width: 250px; max-width: 300px;">
        <div class="sidebar-card">
          <h3 class="sidebar-card-title">Filters</h3>
          <form method="GET" action="/explore" id="explore-filter-form">
            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="search" style="font-size: 0.85rem; font-weight: 600; color: var(--text-body);">Search</label>
              <input type="text" id="search" name="search" value="{{ search }}" placeholder="Search projects..." style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 0.5rem; background: var(--input-bg); color: var(--text-main);">
            </div>
            
            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="level" style="font-size: 0.85rem; font-weight: 600; color: var(--text-body);">Level</label>
              <div class="select-wrap" style="width: 100%;">
                <select id="level" name="level">
                  <option value="">Any Level</option>
                  {% for l in available_levels %}
                  <option value="{{ l | lower }}" {% if level == l | lower %}selected{% endif %}>{{ l }}</option>
                  {% end从业%}
                  <!-- wait, loop end is wrong in python string, let's fix below -->
                </select>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="interest" style="font-size: 0.85rem; font-weight: 600; color: var(--text-body);">Interest</label>
              <div class="select-wrap" style="width: 100%;">
                <select id="interest" name="interest">
                  <option value="">Any Interest</option>
                  <!-- We can hardcode standard interests or pass them -->
                  <option value="web" {% if interest == "web" %}selected{% endif %}>Web Development</option>
                  <option value="data" {% if interest == "data" %}selected{% endif %}>Data and Analytics</option>
                  <option value="education" {% if interest == "education" %}selected{% endif %}>Education Tools</option>
                  <option value="automation" {% if interest == "automation" %}selected{% endif %}>Automation</option>
                  <option value="games" {% if interest == "games" %}selected{% endif %}>Games</option>
                  <option value="cybersecurity" {% if interest == "cybersecurity" %}selected{% endif %}>CyberSecurity/Ethical Hacking</option>
                  <option value="devops" {% if interest == "devops" %}selected{% endif %}>DevOps / Cloud Computing</option>
                  <option value="backend" {% if interest == "backend" %}selected{% endif %}>Backend APIs</option>
                  <option value="tools" {% if interest == "tools" %}selected{% endif %}>Developer Tools</option>
                  <option value="productivity" {% if interest == "productivity" %}selected{% endif %}>Productivity</option>
                  <option value="business logic" {% if interest == "business logic" %}selected{% endif %}>Business Logic</option>
                  <option value="mobile" {% if interest == "mobile" %}selected{% endif %}>Mobile Development</option>
                  <option value="machine learning/ai" {% if interest == "machine learning/ai" %}selected{% endif %}>Machine Learning/AI</option>
                </select>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="time" style="font-size: 0.85rem; font-weight: 600; color: var(--text-body);">Time Availability</label>
              <div class="select-wrap" style="width: 100%;">
                <select id="time" name="time">
                  <option value="">Any Time</option>
                  <option value="low" {% if time == "low" %}selected{% endif %}>Low (Few hours/week)</option>
                  <option value="medium" {% if time == "medium" %}selected{% endif %}>Medium (Weekends)</option>
                  <option value="high" {% if time == "high" %}selected{% endif %}>High (Daily)</option>
                </select>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.5rem;">
              <label for="sort" style="font-size: 0.85rem; font-weight: 600; color: var(--text-body);">Sort By</label>
              <div class="select-wrap" style="width: 100%;">
                <select id="sort" name="sort">
                  <option value="id_asc" {% if sort == "id_asc" %}selected{% endif %}>Default</option>
                  <option value="title_asc" {% if sort == "title_asc" %}selected{% endif %}>Title (A-Z)</option>
                  <option value="title_desc" {% if sort == "title_desc" %}selected{% endif %}>Title (Z-A)</option>
                  <option value="id_desc" {% if sort == "id_desc" %}selected{% endif %}>Newest First</option>
                </select>
              </div>
            </div>

            <button type="submit" class="btn-primary" style="width: 100%;">Apply Filters</button>
            <a href="/explore" class="btn-clear" style="display: block; text-align: center; margin-top: 10px; width: 100%; box-sizing: border-box; text-decoration: none;">Clear Filters</a>
          </form>
        </div>
      </aside>

      <!-- Main Results -->
      <section style="flex: 3; min-width: 300px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h2 style="font-size: 1.25rem;">Showing {{ projects|length }} of {{ total_items }} projects</h2>
        </div>

        {% if projects %}
        <div class="results-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem;">
          {% for project in projects %}
          <div class="project-card">
            <h3 class="project-card-title">{{ project.title }}</h3>
            <p class="project-card-desc"><span class="project-card-desc-text">{{ project.description | truncate(120) }}</span></p>
            <div class="project-card-tags">
              {% for skill in project.skills %}
              <span class="project-tag project-tag--skill">{{ skill }}</span>
              {% endfor %}
              <span class="project-tag project-tag--{{ project.level | lower | replace(' ', '-') }}">{{ project.level }}</span>
              <span class="project-tag project-tag--time">Time: {{ project.time }}</span>
            </div>
            <div class="project-card-footer">
              <a href="/project/{{ project.id }}" class="btn-view-project" style="flex: 1; text-align: center;">View Project &rarr;</a>
            </div>
          </div>
          {% endfor %}
        </div>

        <!-- Pagination Controls -->
        <div class="pagination" style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 3rem;">
          {% if page > 1 %}
          <a href="/explore?page={{ page - 1 }}&per_page=12&search={{ search }}&level={{ level }}&interest={{ interest }}&time={{ time }}&sort={{ sort }}" class="btn-view-code-sm" style="text-decoration: none;">&larr; Previous</a>
          {% else %}
          <span class="btn-view-code-sm" style="opacity: 0.5; cursor: not-allowed;">&larr; Previous</span>
          {% endif %}
          
          <span style="font-weight: 600; color: var(--text-body);">Page {{ page }} of {{ total_pages }}</span>
          
          {% if page < total_pages %}
          <a href="/explore?page={{ page + 1 }}&per_page=12&search={{ search }}&level={{ level }}&interest={{ interest }}&time={{ time }}&sort={{ sort }}" class="btn-view-code-sm" style="text-decoration: none;">Next &rarr;</a>
          {% else %}
          <span class="btn-view-code-sm" style="opacity: 0.5; cursor: not-allowed;">Next &rarr;</span>
          {% endif %}
        </div>
        {% else %}
        <div class="empty-state">
          <h3>No Projects Found</h3>
          <p>Try adjusting your filters or search term.</p>
          <a href="/explore" class="btn-try-again">Clear Filters</a>
        </div>
        {% endif %}
      </section>
    </div>
  </main>
"""
    new_body = new_body.replace("{% end从业%}", "{% endfor %}")
    content = content[:start_idx] + new_body + content[end_idx:]

with open("src/templates/explore.html", "w") as f:
    f.write(content)

print("Done")
