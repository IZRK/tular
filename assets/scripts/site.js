(() => {
  "use strict";

  document.documentElement.classList.add("js");

  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.querySelector("#navigation");

  function closeMenu() {
    menuButton.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
  }

  menuButton?.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(isOpen));
    navigation.classList.toggle("is-open", isOpen);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton?.getAttribute("aria-expanded") === "true") {
      closeMenu();
      menuButton.focus();
    }
  });

  const form = document.querySelector(".archive-tools");
  if (!form) return;

  form.hidden = false;
  const search = form.querySelector("#archive-search");
  const yearSelect = form.querySelector("#archive-year");
  const status = form.querySelector("#search-status");
  const groups = [...document.querySelectorAll(".publication-year")];
  const emptyState = document.querySelector(".no-results");
  const isSlovenian = document.documentElement.lang === "sl";

  function normalize(value) {
    return value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  const records = [...document.querySelectorAll(".publication")].map((element) => ({
    element,
    year: element.closest(".publication-year").dataset.year,
    text: normalize(element.textContent),
  }));

  function filterEntries() {
    const terms = normalize(search.value).split(" ").filter(Boolean);
    const selectedYear = yearSelect.value;
    let count = 0;

    for (const record of records) {
      const yearMatches = !selectedYear || record.year === selectedYear;
      const textMatches = terms.every((term) => record.text.includes(term));
      const visible = yearMatches && textMatches;
      record.element.hidden = !visible;
      if (visible) count += 1;
    }

    for (const group of groups) {
      group.hidden = !group.querySelector(".publication:not([hidden])");
    }

    emptyState.hidden = count !== 0;
    status.textContent = isSlovenian
      ? `Prikazane objave: ${count} od ${records.length}`
      : `Showing ${count} of ${records.length} entries`;
  }

  search.addEventListener("input", filterEntries);
  yearSelect.addEventListener("change", filterEntries);
  form.addEventListener("submit", (event) => event.preventDefault());
  form.addEventListener("reset", () => {
    requestAnimationFrame(() => {
      filterEntries();
      search.focus();
    });
  });
  filterEntries();
})();
