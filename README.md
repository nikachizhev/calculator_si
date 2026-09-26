# Calculator SI

Веб-калькулятор на Python и Flask. Выражения вычисляются на сервисе безопасным
парсером, а успешные расчёты сохраняются в SQLite отдельно для каждого клиента.

Возможности:

- операции `+`, `-`, `*`, `/`, `%`, степень `^` и скобки;
- функции `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `log`, `ln`,
  `exp`, `abs`, `floor`, `ceil`, `degrees`, `radians`, `factorial`;
- математические константы `pi` и `e` (тригонометрия использует радианы);
- понятные ответы API при неверном выражении;
- история последних 100 вычислений;
- повторный ввод выражения кликом по истории;
- адаптивный веб-интерфейс.

## Структура проекта

```text
app.py                              # точка запуска
calculator_app/
├── __init__.py                     # фабрика Flask-приложения
├── routes.py                       # веб-страница и JSON API
├── database.py                     # хранение истории в SQLite
└── services/
    └── calculator.py               # вычисление выражений
static/                             # JavaScript и CSS
templates/                          # HTML-шаблоны
tests/
├── test_service.py                 # тесты вычислителя
├── test_security.py                # тесты безопасности парсера
├── test_api.py                     # тесты HTTP API
└── test_database.py                # тесты SQLite
```

## Распределение работы в команде

1. **Разработчик вычислений** — `calculator_app/services/calculator.py`:
   операции, функции, ограничения вычислений и сообщения об ошибках.
2. **Frontend-разработчик** — `templates/` и `static/`:
   адаптивная раскладка, история и обработка действий пользователя.
3. **Backend-разработчик** — `calculator_app/routes.py`, `database.py`, `__init__.py`:
   API, SQLite, разделение клиентов.
4. **QA вычислений и безопасности** — `tests/test_service.py`,
   `tests/test_security.py`: корректность математики, граничные значения и запрет
   исполнения произвольного кода.
5. **QA API и данных** — `tests/test_api.py`, `tests/test_database.py`:
   HTTP-сценарии, изоляция клиентов, порядок истории и операции с базой.

## Запуск

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Откройте <http://127.0.0.1:5000>.

## Тесты

```powershell
python -m unittest discover -s tests
```
