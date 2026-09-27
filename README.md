# Calculator

Веб-калькулятор на Python и Django. Выражения вычисляются на сервисе безопасным парсером, а успешные расчёты сохраняются в базу данных отдельно для каждого клиента.

Возможности:

- операции `+`, `-`, `*`, `/`, `%`, степень `^` и скобки;
- функции `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `log`, `ln`,
  `exp`, `abs`, `floor`, `ceil`, `degrees`, `radians`, `factorial`;
- математические константы `pi` и `e` (тригонометрия использует радианы);
- понятные ответы API при неверном выражении;
- история последних 100 вычислений;
- повторный ввод выражения кликом по истории;

## Структура проекта

```text
manage.py                           # команды Django
src/
├── config/                         # конфигурация всего Django-проекта
│   ├── settings.py                 # настройки проекта
│   ├── urls.py                     # корневые маршруты
│   └── wsgi.py                     # точка входа веб-сервера
├── calculator/                     # приложение калькулятора
│   ├── models.py                   # ORM-модель вычисления
│   ├── views.py                    # веб-страница и JSON API
│   ├── urls.py                     # маршруты приложения
│   ├── admin.py                    # управление историей в Django Admin
│   ├── migrations/                 # схема базы данных
│   ├── services/evaluator.py       # вычисление выражений
│   └── tests/                      # все автоматические тесты
├── static/                         # JavaScript и CSS
└── templates/                      # HTML-шаблоны
```

## Запуск (на windows)

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Откройте <http://127.0.0.1:8000>.

## Тесты

```powershell
.\.venv\Scripts\python.exe manage.py test calculator
```

Для доступа к истории через Django Admin создайте администратора командой
`.\.venv\Scripts\python.exe manage.py createsuperuser`, затем откройте
<http://127.0.0.1:8000/admin/>.
