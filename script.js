let allJobs = [];
let currentFilter = "All";

const jobsGrid = document.getElementById("jobsGrid");
const searchInput = document.getElementById("searchInput");
const jobCount = document.getElementById("jobCount");
const lastUpdated = document.getElementById("lastUpdated");
const filters = document.getElementById("filters");

async function loadJobs() {
  try {
    const response = await fetch("jobs.json?t=" + Date.now());
    allJobs = await response.json();
    renderJobs();
    lastUpdated.textContent = "Last checked: " + new Date().toLocaleDateString();
  } catch (error) {
    jobsGrid.innerHTML = `<p>Could not load jobs.json.</p>`;
  }
}

function renderJobs() {
  const query = searchInput.value.toLowerCase().trim();
  const filtered = allJobs.filter(job => {
    const text = [job.title, job.organization, job.department, job.location, job.level, job.category].join(" ").toLowerCase();
    return text.includes(query) && (currentFilter === "All" || job.category === currentFilter);
  });

  jobCount.textContent = `${filtered.length} opportunities found`;

  if (!filtered.length) {
    jobsGrid.innerHTML = `<p>No matching jobs right now.</p>`;
    return;
  }

  jobsGrid.innerHTML = filtered.map(job => `
    <article class="job-card">
      <div>
        <div class="card-top">
          ${job.is_new ? `<span class="tag new">NEW</span>` : ""}
          <span class="tag">${escapeHTML(job.category || "Opportunity")}</span>
          <span class="tag">${escapeHTML(job.source || "UN")}</span>
        </div>
        <h2 class="job-title">${escapeHTML(job.title || "Untitled role")}</h2>
        <p class="meta">${escapeHTML(job.organization || "UN")} · ${escapeHTML(job.location || "Location not listed")}</p>
        <p class="meta">${escapeHTML(job.level || "Level not listed")}</p>
        <p class="deadline">Deadline: ${escapeHTML(job.deadline || "Not listed")}</p>
      </div>
      <a class="job-link" href="${job.link}" target="_blank" rel="noopener">View role →</a>
    </article>
  `).join("");
}

function escapeHTML(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

searchInput.addEventListener("input", renderJobs);
filters.addEventListener("click", event => {
  if (!event.target.matches("button")) return;
  document.querySelectorAll(".filters button").forEach(button => button.classList.remove("active"));
  event.target.classList.add("active");
  currentFilter = event.target.dataset.filter;
  renderJobs();
});

loadJobs();
