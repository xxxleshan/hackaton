const baseUrl = 'http://localhost:8000';
let token = '';

// === Таб-меню ===
const tabs = document.querySelectorAll('nav button');
tabs.forEach(btn =>
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    tabs.forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    document.querySelectorAll('.tab').forEach(sec =>
      sec.classList.toggle('active', sec.id === tab)
    );
  })
);
function enableDashboard() {
  const dashBtn = document.querySelector('[data-tab="dashboard"]');
  dashBtn.disabled = false;
  dashBtn.style.display = 'block';
  dashBtn.click();
}

// === Субсекции дашборда ===
document.querySelectorAll('.buttons button').forEach(btn =>
  btn.addEventListener('click', () => {
    const sec = btn.dataset.section;
    document.querySelectorAll('.subsection').forEach(s =>
      s.classList.remove('active')
    );
    document.getElementById(sec).classList.add('active');
  })
);

// === Регистрация ===
document.getElementById('form-register').addEventListener('submit', async e => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target));
  const res = await fetch(`${baseUrl}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  document.getElementById('regOutput').textContent = JSON.stringify(
    await res.json(),
    null,
    2
  );
});

// === Вход ===
document.getElementById('form-login').addEventListener('submit', async e => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target));
  const res = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  document.getElementById('loginOutput').textContent = JSON.stringify(
    data,
    null,
    2
  );
  if (data.access_token) {
    token = data.access_token;
    enableDashboard();
  }
});

// === Загрузка чека ===
document.getElementById('btnUpload').addEventListener('click', async () => {
  const file = document.getElementById('uploadFile').files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${baseUrl}/receipts/upload`, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + token },
    body: form
  });
  document.getElementById('uploadOutput').textContent = JSON.stringify(
    await res.json(),
    null,
    2
  );
});

// === Хелпер для авторизованных запросов ===
async function getJSON(path) {
  const res = await fetch(baseUrl + path, {
    headers: { Authorization: 'Bearer ' + token }
  });
  return res.json();
}

// === Таблица чеков ===
async function loadReceipts() {
  const data = await getJSON('/receipts/');
  const tbody = document.querySelector('#receiptsTable tbody');
  tbody.innerHTML = '';
  data.receipts?.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.id}</td>
      <td>${r.store}</td>
      <td>${r.total_amount}</td>
      <td>${new Date(r.purchase_date).toLocaleString()}</td>
    `;
    tbody.appendChild(tr);
  });
}

// === Статистика: диаграммы уменьшенного размера ===
let chartCategories, chartMonthly;
async function loadStatsCategories() {
  const data = await getJSON('/stats/categories');
  const labels = data.stats.map(s => s.category);
  const values = data.stats.map(s => s.total);
  const canvas = document.getElementById('chartCategories');
  canvas.style.width = '30%';
  if (chartCategories) chartCategories.destroy();
  chartCategories = new Chart(canvas, {
    type: 'pie',
    data: { labels, datasets: [{ data: values }] },
    options: { responsive: true }
  });
}
async function loadStatsMonthly() {
  const data = await getJSON('/stats/monthly');
  const labels = data.stats.map(s => s.month);
  const values = data.stats.map(s => s.total);
  const canvas = document.getElementById('chartMonthly');
  canvas.style.width = '30%';
  if (chartMonthly) chartMonthly.destroy();
  chartMonthly = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{ label: 'Траты по месяцам', data: values, fill: false }]
    },
    options: { responsive: true }
  });
}

// === Рекомендации: список лучших категорий ===
async function loadRecs() {
  const data = await getJSON('/recommendations/');
  const section = document.getElementById('recs');
  // спрячем старый canvas
  const canvas = document.getElementById('chartRecs');
  if (canvas) canvas.style.display = 'none';
  // уберём предыдущий список
  const oldUl = section.querySelector('ul');
  if (oldUl) oldUl.remove();
  // создаём новый список
  const ul = document.createElement('ul');
  data.recommendations.forEach(r => {
    const li = document.createElement('li');
    li.textContent = `${r.category_name}: вы могли бы получить ${r.expected_cashback} ₽`;
    ul.appendChild(li);
  });
  section.appendChild(ul);
}

// === Автозагрузка при переключении ===
document
  .querySelector('[data-section="receipts"]')
  .addEventListener('click', loadReceipts);
document
  .querySelector('[data-section="stats"]')
  .addEventListener('click', () => {
    loadStatsCategories();
    loadStatsMonthly();
  });
document
  .querySelector('[data-section="recs"]')
  .addEventListener('click', loadRecs);
