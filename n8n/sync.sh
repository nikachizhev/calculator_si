#!/usr/bin/env bash
# Sync n8n workflows between this repo and a running n8n instance.
#
#   n8n/sync.sh push [file...]   upload repo JSON to n8n and publish it (default: all)
#   n8n/sync.sh pull             download all n8n workflows into n8n/workflows/
#
# Workflows are matched by name. Reads N8N_API_URL and N8N_API_KEY from ../.env.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKFLOWS_DIR="$ROOT/n8n/workflows"
[[ -f "$ROOT/.env" ]] && set -a && source "$ROOT/.env" && set +a
: "${N8N_API_URL:?set N8N_API_URL in .env}"
: "${N8N_API_KEY:?set N8N_API_KEY in .env}"

api() {
    local method=$1 path=$2
    shift 2
    curl -sS --fail-with-body -X "$method" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" -H "Content-Type: application/json" \
        "$N8N_API_URL/api/v1$path" "$@"
}

# Only fields (and settings) the public API accepts on create/update.
EDITABLE='{name, nodes, connections, settings: (
    (.settings // {}) | with_entries(select(.key | IN(
        "executionOrder", "timezone", "saveDataSuccessExecution", "saveDataErrorExecution",
        "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "errorWorkflow",
        "callerPolicy", "callerIds"))) | .executionOrder //= "v1"
)}'

slug() { tr '[:upper:]' '[:lower:]' <<<"$1" | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g'; }

push() {
    local file=$1 name id
    name=$(jq -r .name "$file")
    id=$(api GET "/workflows?limit=250" | jq -r --arg n "$name" '.data[] | select(.name == $n and (.isArchived | not)) | .id' | head -1)

    if [[ -n "$id" ]]; then
        jq "$EDITABLE" "$file" | api PUT "/workflows/$id" --data @- >/dev/null
        echo "updated  $name ($id)"
    else
        id=$(jq "$EDITABLE" "$file" | api POST "/workflows" --data @- | jq -r .id)
        echo "created  $name ($id)"
    fi

    # Re-activating forces n8n to re-register webhooks with the new version.
    api POST "/workflows/$id/deactivate" >/dev/null || true
    if api POST "/workflows/$id/activate" >/dev/null 2>&1; then
        echo "published $name"
    else
        echo "saved (not published: workflow has no activatable trigger) $name"
    fi
}

pull() {
    mkdir -p "$WORKFLOWS_DIR"
    api GET "/workflows?limit=250" | jq -c '.data[] | select(.isArchived | not)' | while read -r wf; do
        local name
        name=$(jq -r .name <<<"$wf")
        jq "$EDITABLE" <<<"$wf" >"$WORKFLOWS_DIR/$(slug "$name").json"
        echo "pulled   $name"
    done
}

case "${1:-}" in
    push)
        shift
        files=("$@")
        [[ ${#files[@]} -eq 0 ]] && files=("$WORKFLOWS_DIR"/*.json)
        for f in "${files[@]}"; do push "$f"; done
        ;;
    pull) pull ;;
    *) echo "usage: $0 push [file...] | pull" >&2; exit 1 ;;
esac
