'use strict';
const grid = document.querySelector('#repo-grid');
const cards = Array.from(grid.children);
const search = document.querySelector('#search');
const language = document.querySelector('#language');
const sort = document.querySelector('#sort');
const active = document.querySelector('#active');
const results = document.querySelector('#results');
const empty = document.querySelector('#empty');
function update() {
  const query = search.value.trim().toLocaleLowerCase();
  const ordered = [...cards].sort((a, b) => {
    if (sort.value === 'name') return a.dataset.name.localeCompare(b.dataset.name);
    if (sort.value === 'stars') return Number(b.dataset.stars) - Number(a.dataset.stars) || a.dataset.name.localeCompare(b.dataset.name);
    return b.dataset.updated.localeCompare(a.dataset.updated) || a.dataset.name.localeCompare(b.dataset.name);
  });
  let count = 0;
  for (const card of ordered) {
    card.hidden = !((!query || card.dataset.search.toLocaleLowerCase().includes(query)) &&
      (!language.value || card.dataset.language === language.value) &&
      (!active.checked || card.dataset.archived === 'false'));
    if (!card.hidden) count++;
    grid.append(card);
  }
  results.textContent = `${count} of ${cards.length} repositories`;
  empty.hidden = count !== 0;
}
search.addEventListener('input', update);
for (const control of [language, sort, active]) control.addEventListener('change', update);
document.querySelector('#reset').addEventListener('click', () => {
  search.value = ''; language.value = ''; sort.value = 'updated'; active.checked = false;
  update(); search.focus();
});
document.querySelector('#filters').hidden = false;
update();
