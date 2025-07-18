let allResults = [];
let filteredResults = [];
let currentPage = 1;
let resultsPerPage = 10;

function fetchData() {
  fetch("docs/toto_result.json")
    .then((response) => response.json())
    .then((data) => {
      allResults = data;
      document.getElementById("lastUpdated").textContent = new Date().toLocaleString();
      applyFilters();
    })
    .catch((error) => {
      console.error("[ERROR] Failed to load JSON:", error);
    });
}

function applyFilters() {
  const dateValue = document.getElementById("dateFilter").value;
  const drawValue = document.getElementById("drawFilter").value.trim();

  filteredResults = allResults.filter((entry) => {
    const matchesDate = !dateValue || new Date(entry.date).toISOString().slice(0, 10) === dateValue;
    const matchesDraw = !drawValue || entry.draw_number === drawValue;
    return matchesDate && matchesDraw;
  });

  currentPage = 1;
  renderResults();
}

function updatePagination() {
  resultsPerPage = parseInt(document.getElementById("perPageSelect").value, 10);
  currentPage = 1;
  renderResults();
}

function renderResults() {
  const tableContainer = document.getElementById("resultsTableContainer");
  tableContainer.innerHTML = "";

  const totalPages = Math.ceil(filteredResults.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const endIndex = startIndex + resultsPerPage;
  const paginatedResults = filteredResults.slice(startIndex, endIndex);

  if (paginatedResults.length === 0) {
    tableContainer.innerHTML = "<p>No results found.</p>";
    document.getElementById("paginationControls").innerHTML = "";
    return;
  }

  const table = document.createElement("table");
  table.className = "results-table";

  const thead = document.createElement("thead");
  thead.innerHTML = `
    <tr>
      <th>Date</th>
      <th>Draw Number</th>
      <th>Winning Numbers</th>
      <th>Additional Number</th>
      <th>Jackpot</th>
    </tr>`;
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  paginatedResults.forEach((result) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${result.date}</td>
      <td>${result.draw_number}</td>
      <td>${result.winning_numbers.join(", ")}</td>
      <td>${result.additional_number}</td>
      <td>${result.jackpot}</td>
    `;
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  tableContainer.appendChild(table);

  renderPaginationControls(totalPages);
}

function renderPaginationControls(totalPages) {
  const container = document.getElementById("paginationControls");
  container.innerHTML = "";

  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = i === currentPage ? "active-page" : "";
    btn.onclick = () => {
      currentPage = i;
      renderResults();
    };
    container.appendChild(btn);
  }
}

function resetFilters() {
  document.getElementById("dateFilter").value = "";
  document.getElementById("drawFilter").value = "";
  applyFilters();
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

document.addEventListener("DOMContentLoaded", () => {
  fetchData();
});
