const display = document.querySelector('#display');
const message = document.querySelector('#message');
const historyList = document.querySelector('#history-list');
const emptyHistory = document.querySelector('#empty-history');
const clientId = getClientId();

function getClientId() {
  let id = localStorage.getItem('calculator-client-id');
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem('calculator-client-id', id);
  }
  return id;
}

async function loadHistory() {
  const response = await fetch(`/api/history?client_id=${encodeURIComponent(clientId)}`);
  const items = await response.json();
  historyList.replaceChildren(...items.map((item) => {
    const entry = document.createElement('li');
    const button = document.createElement('button');
    button.className = 'history-item';
    button.type = 'button';
    const expression = document.createElement('span');
    expression.className = 'history-expression';
    expression.textContent = item.expression;
    const result = document.createElement('strong');
    result.className = 'history-result';
    result.textContent = `= ${item.result}`;
    button.append(expression, result);
    button.addEventListener('click', () => {
      display.value = item.expression;
      display.focus();
    });
    entry.append(button);
    return entry;
  }));
  emptyHistory.hidden = items.length > 0;
}

async function calculate() {
  message.textContent = '';
  try {
    const response = await fetch('/api/calculate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({expression: display.value, client_id: clientId}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    display.value = data.result;
    await loadHistory();
  } catch (error) {
    message.textContent = error.message || 'Не удалось вычислить выражение';
  }
}

document.querySelector('.keys').addEventListener('click', (event) => {
  const button = event.target.closest('button');
  if (!button) return;
  if (button.dataset.value) display.value += button.dataset.value;
  if (button.dataset.action === 'clear') display.value = '';
  if (button.dataset.action === 'backspace') display.value = display.value.slice(0, -1);
  if (button.dataset.action === 'calculate') calculate();
  message.textContent = '';
  display.focus();
});

function insertFunction(event) {
  const button = event.target.closest('button');
  if (!button) return;
  const start = display.selectionStart ?? display.value.length;
  const end = display.selectionEnd ?? start;
  display.setRangeText(button.dataset.insert, start, end, 'end');
  message.textContent = '';
  display.focus();
}

document.querySelector('.scientific-keys').addEventListener('click', insertFunction);
document.querySelector('.more-function-keys').addEventListener('click', insertFunction);

display.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    calculate();
  }
  if (event.key === 'Escape') {
    display.value = '';
    message.textContent = '';
  }
});

document.querySelector('#refresh').addEventListener('click', loadHistory);
document.querySelector('#clear-history').addEventListener('click', async () => {
  if (!confirm('Очистить всю историю вычислений?')) return;
  await fetch('/api/history', {
    method: 'DELETE',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({client_id: clientId}),
  });
  await loadHistory();
});
loadHistory().catch(() => { message.textContent = 'Не удалось загрузить историю'; });
