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
calculator-si/
├── manage.py                       # команды Django
├── requirements.txt                # зависимости Python
├── README.md                       # документация проекта
├── .gitignore                      # файлы, исключённые из Git
├── instance/
│   └── calculator.db               # локальная SQLite-база (не загружается в Git)
│
src/
├── config/                         # конфигурация всего Django-проекта
│   ├── __init__.py                 # обозначает Python-пакет
│   ├── settings.py                 # настройки проекта
│   ├── urls.py                     # корневые маршруты
│   └── wsgi.py                     # точка входа веб-сервера
├── calculator/                     # приложение калькулятора
│   ├── __init__.py                 # обозначает Python-пакет
│   ├── apps.py                     # конфигурация Django-приложения
│   ├── admin.py                    # управление историей в Django Admin
│   ├── models.py                   # ORM-модель вычисления
│   ├── views.py                    # веб-страница и JSON API
│   ├── urls.py                     # маршруты приложения
│   ├── migrations/                 # история схемы базы данных
│   │   ├── __init__.py
│   │   └── 0001_initial.py         # создание таблицы вычислений
│   ├── services/                   # бизнес-логика
│   │   ├── __init__.py
│   │   └── evaluator.py            # безопасное вычисление выражений
│   └── tests/                      # автоматические тесты
│       ├── __init__.py
│       ├── test_evaluator.py       # арифметика и научные функции
│       ├── test_security.py        # безопасность парсера
│       ├── test_models.py          # модель и Django ORM
│       └── test_views.py           # страницы и JSON API
├── static/
│   ├── app.js                      # логика браузерного клиента
│   └── style.css                   # оформление интерфейса
└── templates/
    └── index.html                  # страница калькулятора
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
