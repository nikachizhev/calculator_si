#!/usr/bin/env bash
# Smoke test for the calculator's n8n workflows. Needs n8n and Django running.
#
#   n8n/test.sh          check webhooks + scheduled workflows (errors in the last 24h)
#   SINCE_HOURS=2 n8n/test.sh
#
# Test data is written as client "n8n-test", which the nightly cleanup deletes.
# Exits non-zero if any check fails.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[[ -f "$ROOT/.env" ]] && set -a && source "$ROOT/.env" && set +a
: "${N8N_API_URL:?set N8N_API_URL in .env}"
: "${N8N_API_KEY:?set N8N_API_KEY in .env}"
HOOK="${N8N_WEBHOOK_URL:-$N8N_API_URL/webhook}"
SINCE_HOURS="${SINCE_HOURS:-24}"
CLIENT="n8n-test"

passed=0
failed=0
if [[ -t 1 ]]; then OK=$'\e[32mPASS\e[0m' KO=$'\e[31mFAIL\e[0m'; else OK=PASS KO=FAIL; fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# check <description> <command...>: runs the command, records pass/fail.
check() {
    local description=$1
    shift
    if "$@" >/dev/null 2>&1; then
        printf '  %s %s\n' "$OK" "$description"
        passed=$((passed + 1))
    else
        printf '  %s %s\n' "$KO" "$description"
        [[ -s "$TMP/body" ]] && printf '       status %s, body: %.300s\n' "$STATUS" "$(tr -d '\n' <"$TMP/body")"
        failed=$((failed + 1))
    fi
}

# call <method> <path> [curl args...]: sets STATUS, writes the body to $TMP/body.
call() {
    local method=$1 path=$2
    shift 2
    STATUS=$(curl -sS -m 15 -o "$TMP/body" -w '%{http_code}' -X "$method" "$HOOK/$path" "$@" 2>/dev/null)
}
post_json() { call POST "$1" -H 'Content-Type: application/json' -d "$2"; }
status_is() { [[ "$STATUS" == "$1" ]]; }
body_has() { jq -e "$1" "$TMP/body"; }

api() { curl -sS -m 15 -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_API_URL/api/v1$1"; }

echo "Webhooks ($HOOK)"

post_json calculate "{\"expression\": \"2+2\", \"client_id\": \"$CLIENT\"}"
check "calculate: 2+2 = 4" eval 'status_is 200 && body_has ".result == 4"'
post_json calculate "{\"expression\": \"1/0\", \"client_id\": \"$CLIENT\"}"
check "calculate: 1/0 -> 400 with error" eval 'status_is 400 && body_has ".error | length > 0"'

post_json batch "{\"expressions\": [\"2^10\", \"sqrt(16)\", \"1/0\"], \"client_id\": \"$CLIENT\"}"
check "batch: 3 expressions, 2 ok, 1 failed" \
    eval 'status_is 200 && body_has ".count == 3 and .succeeded == 2 and .failed == 1 and .results[0].result == 1024"'
post_json batch '{"expressions": []}'
check "batch: empty list -> 400" status_is 400

call POST "csv?client_id=$CLIENT" -F "file=@$ROOT/n8n/examples/expressions.csv"
csv_ok() {
    sed '1s/^\xEF\xBB\xBF//' "$TMP/body" >"$TMP/csv"
    [[ "$(head -1 "$TMP/csv")" == "expression,result,error" ]] &&
        [[ $(($(wc -l <"$TMP/csv") + 1)) -eq $(wc -l <"$ROOT/n8n/examples/expressions.csv") ]] &&
        grep -qx '2 + 3 \* 4,14,' "$TMP/csv"
}
check "csv: sample file -> results.csv with one row per input" eval 'status_is 200 && csv_ok'
call POST csv -F "other=@$ROOT/n8n/examples/expressions.csv"
check "csv: missing 'file' field -> 400" status_is 400

post_json safe-calculate "{\"expression\": \"sqrt(16)\", \"client_id\": \"$CLIENT\"}"
check "gateway: sqrt(16) allowed = 4" eval 'status_is 200 && body_has ".result == 4"'
post_json safe-calculate "{\"expression\": \"import os\", \"client_id\": \"$CLIENT\"}"
check "gateway: 'import os' rejected before Django" eval 'status_is 400 && body_has ".error | startswith(\"unknown names\")"'

call GET "stats?client_id=$CLIENT"
check "stats: counts calculations and functions" \
    eval 'status_is 200 && body_has ".calculations > 0 and (.functions | type == \"object\")"'

echo
echo "Scheduled workflows (errors in the last ${SINCE_HOURS}h)"

: >"$TMP/body"  # no webhook body to show for these checks
since=$(date -u -d "-${SINCE_HOURS} hours" +%Y-%m-%dT%H:%M:%S)
workflows=$(api "/workflows?limit=250")
for name in "Calculator: health monitor" "Calculator: regression checker" "Calculator: nightly cleanup"; do
    id=$(jq -r --arg n "$name" '.data[] | select(.name == $n and (.isArchived | not)) | .id' <<<"$workflows" | head -1)
    check "$name: exists and is active" \
        jq -e --arg n "$name" '.data[] | select(.name == $n and (.isArchived | not)) | .active' <<<"$workflows"
    [[ -z "$id" ]] && continue
    last_error=$(api "/executions?workflowId=$id&status=error&limit=1" | jq -r '.data[0].startedAt // ""')
    : >"$TMP/body"
    check "$name: no failed runs since $since UTC${last_error:+ (last failure $last_error)}" \
        test -z "$last_error" -o "$last_error" \< "$since"
done

echo
echo "$passed passed, $failed failed"
[[ $failed -eq 0 ]]
