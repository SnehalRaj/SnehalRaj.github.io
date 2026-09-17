// add bootstrap classes to tables (vanilla JS)
document.addEventListener("DOMContentLoaded", function() {
  var tables = document.querySelectorAll("table");
  var isDark = document.documentElement.getAttribute("data-theme") === "dark";

  tables.forEach(function(table) {
    if (isDark) {
      table.classList.add("table-dark");
    } else {
      table.classList.remove("table-dark");
    }

    // only select tables that are not inside an element with "news" (about page) or "card" (cv page) class
    if (!table.closest('[class*="news"]') &&
        !table.closest('[class*="card"]') &&
        !table.closest("code")) {
      table.setAttribute("data-toggle", "table");
      table.classList.add("table-hover");
    }
  });
});

