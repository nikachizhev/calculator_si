import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from calculator.models import Calculation
from calculator.services.evaluator import CalculationError, calculate


def _json_body(request) -> dict:
    try:
        value = json.loads(request.body or b"{}")
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _client_id(value: object) -> str:
    return str(value or "anonymous")[:100]


@require_GET
def index(request):
    return render(request, "index.html")


@csrf_exempt
@require_POST
def api_calculate(request):
    payload = _json_body(request)
    expression = payload.get("expression", "")
    client_id = _client_id(payload.get("client_id"))
    try:
        result = calculate(expression)
    except CalculationError as error:
        return JsonResponse({"error": str(error)}, status=400)

    calculation = Calculation.objects.create(
        client_id=client_id, expression=expression, result=str(result)
    )
    return JsonResponse({"id": calculation.id, "result": result})


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def api_history(request):
    if request.method == "DELETE":
        client_id = _client_id(_json_body(request).get("client_id"))
        deleted, _ = Calculation.objects.filter(client_id=client_id).delete()
        return JsonResponse({"deleted": deleted})

    client_id = _client_id(request.GET.get("client_id"))
    history = Calculation.objects.filter(client_id=client_id).values(
        "id", "expression", "result", "created_at"
    )[:100]
    return JsonResponse(list(history), safe=False)


@require_GET
def api_health(request):
    return JsonResponse({"service": "calculator", "status": "ok"})
