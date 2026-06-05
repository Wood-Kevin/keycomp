const REGIONS = ['us', 'eu', 'kr', 'tw'];
const MAX_CHARS = 5;

const rowsContainer  = document.getElementById('character-rows');
const addBtn         = document.getElementById('add-btn');
const analyzeBtn     = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results');
const charCards      = document.getElementById('character-cards');
const analysisText   = document.getElementById('analysis-text');
const errorBanner    = document.getElementById('error-banner');
const loadingEl      = document.getElementById('loading');

// ── Row management ────────────────────────────────────────────────────────────

function regionOptions() {
  return REGIONS.map(r =>
    `<option value="${r}">${r.toUpperCase()}</option>`
  ).join('');
}

function addRow() {
  const row = document.createElement('div');
  row.className = 'char-row';
  row.innerHTML = `
    <select class="f-region" aria-label="Region">${regionOptions()}</select>
    <input class="f-realm"  type="text" placeholder="Realm"     aria-label="Realm">
    <input class="f-name"   type="text" placeholder="Character" aria-label="Character name">
    <button class="remove-btn" type="button" aria-label="Remove">✕</button>
  `;
  row.querySelector('.remove-btn').addEventListener('click', () => {
    row.remove();
    syncButtons();
  });
  rowsContainer.appendChild(row);
  syncButtons();
  row.querySelector('.f-realm').focus();
}

function syncButtons() {
  const count = rowsContainer.children.length;
  addBtn.disabled = count >= MAX_CHARS;
}

function getCharacters() {
  return Array.from(rowsContainer.children).map(row => ({
    region: row.querySelector('.f-region').value,
    realm:  row.querySelector('.f-realm').value.trim(),
    name:   row.querySelector('.f-name').value.trim(),
  }));
}

// ── Rendering ─────────────────────────────────────────────────────────────────

function roleBadge(role) {
  const r = (role || '').toLowerCase();
  if (r === 'tank')   return `<span class="role-badge role-tank">Tank</span>`;
  if (r === 'healer') return `<span class="role-badge role-healer">Healer</span>`;
  return `<span class="role-badge role-dps">DPS</span>`;
}

function renderChar(c) {
  const seasons = c.mythic_plus_scores_by_season || [];
  const score   = seasons[0]?.scores?.all ?? 0;
  const runs    = (c.mythic_plus_recent_runs || []).slice(0, 3);

  const runItems = runs.length
    ? runs.map(r => `
        <li>
          <span class="run-dungeon">${r.dungeon}</span>
          <span class="run-key">+${r.mythic_level}</span>
        </li>`).join('')
    : '<li><span style="color:var(--text-muted)">No recent runs</span></li>';

  const card = document.createElement('div');
  card.className = 'char-card';
  card.innerHTML = `
    <div class="char-card-name">${c.name}</div>
    <div class="char-card-spec">${c.active_spec_name} ${c.class} · ${(c.realm || '').replace(/-/g,' ')} ${(c.region||'').toUpperCase()}</div>
    ${roleBadge(c.active_spec_role)}
    <div class="score-label">M+ Score</div>
    <div class="score-value">${Math.round(score).toLocaleString()}</div>
    <div class="runs-label">Recent Runs</div>
    <ul class="run-list">${runItems}</ul>
  `;
  return card;
}

function showResults(data) {
  charCards.innerHTML = '';
  data.characters.forEach(c => charCards.appendChild(renderChar(c)));
  analysisText.textContent = data.analysis;
  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── API call ──────────────────────────────────────────────────────────────────

function showError(msg) {
  errorBanner.textContent = msg;
  errorBanner.classList.remove('hidden');
}

function clearError() {
  errorBanner.textContent = '';
  errorBanner.classList.add('hidden');
}

async function analyze() {
  clearError();
  resultsSection.classList.add('hidden');

  const characters = getCharacters();

  if (characters.length === 0) {
    showError('Add at least one character before analyzing.');
    return;
  }

  const missing = characters.find(c => !c.realm || !c.name);
  if (missing) {
    showError('Each character needs a realm and a name.');
    return;
  }

  analyzeBtn.disabled = true;
  addBtn.disabled = true;
  loadingEl.classList.remove('hidden');

  try {
    const resp = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ characters }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      showError(data.error || `Server error: ${resp.status}`);
      return;
    }

    showResults(data);
  } catch (err) {
    showError('Could not reach the server. Is Flask running?');
  } finally {
    loadingEl.classList.add('hidden');
    analyzeBtn.disabled = false;
    syncButtons();
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────

addBtn.addEventListener('click', addRow);
analyzeBtn.addEventListener('click', analyze);

// Allow Enter in any input to trigger analyze
rowsContainer.addEventListener('keydown', e => {
  if (e.key === 'Enter') analyze();
});

addRow(); // start with one empty row
