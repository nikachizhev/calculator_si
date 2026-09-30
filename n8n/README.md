# n8n-воркфлоу калькулятора

Воркфлоу хранятся в `workflows/` и синхронизируются с запущенным n8n скриптом `sync.sh`
(настройки `N8N_API_URL` и `N8N_API_KEY` берутся из `../.env`).

```bash
docker run -d --name n8n --restart unless-stopped -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
n8n/sync.sh push        # репозиторий → n8n и публикация (все файлы или указанные)
n8n/sync.sh pull        # n8n → репозиторий (после правок в редакторе n8n)
```

Django должен слушать `0.0.0.0:8000`, а `DJANGO_ALLOWED_HOSTS` — содержать `host.docker.internal`:
из контейнера n8n обращается к нему по адресу `http://host.docker.internal:8000`.

## Вебхуки

| Воркфлоу | Запрос | Что делает |
|---|---|---|
| webhook → API → respond | `POST /webhook/calculate` `{"expression"}` | одно вычисление |
| batch calculate | `POST /webhook/batch` `{"expressions": [...], "client_id"?}` | до 50 выражений за запрос |
| CSV in → CSV out | `POST /webhook/csv?client_id=...` файл в поле `file` | CSV с колонкой `expression` → CSV с `result`/`error` |
| validation gateway | `POST /webhook/safe-calculate` `{"expression", "client_id"?}` | проверка до Django + 10 запросов/мин на клиента |
| stats | `GET /webhook/stats?client_id=...` | статистика по последним 100 вычислениям |

```bash
curl -X POST localhost:5678/webhook/batch -H 'Content-Type: application/json' -d '{"expressions": ["2^10", "1/0"]}'
curl -F "file=@n8n/examples/expressions.csv" localhost:5678/webhook/csv -o results.csv
curl -X POST localhost:5678/webhook/safe-calculate -H 'Content-Type: application/json' -d '{"expression": "sqrt(2)*pi"}'
curl "localhost:5678/webhook/stats?client_id=anonymous"
```

## По расписанию (Europe/Moscow)

| Воркфлоу | Когда | Что делает |
|---|---|---|
| health monitor | каждую минуту | проверяет `/api/health`; сбой — упавшее выполнение (успешные не сохраняются) |
| regression checker | каждый час | считает 13 выражений с известным ответом; расхождение — упавшее выполнение |
| nightly cleanup | в 03:00 | удаляет историю служебных клиентов `n8n-regression` и `n8n-test` |

Упавшие выполнения видны в n8n: **Overview → Executions**, фильтр по статусу *Error*.
