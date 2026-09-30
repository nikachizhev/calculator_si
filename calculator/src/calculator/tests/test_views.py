import json

from django.test import TestCase
from django.urls import reverse

from calculator.models import Calculation


class CalculatorViewTests(TestCase):
    def post_calculation(self, expression, client_id="alice"):
        return self.client.post(
            reverse("api_calculate"),
            data=json.dumps({"expression": expression, "client_id": client_id}),
            content_type="application/json",
        )

    def test_index_renders(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CALCULATOR SERVICE")

    def test_calculation_is_saved(self):
        response = self.post_calculation("sqrt(16) + log(100)")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 6)
        self.assertTrue(Calculation.objects.filter(client_id="alice", result="6.0").exists())

    def test_invalid_expression_is_not_saved(self):
        response = self.post_calculation("(2 + 3")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertFalse(Calculation.objects.exists())

    def test_history_is_isolated_and_newest_first(self):
        for expression in ("1 + 1", "2 + 2", "3 + 3"):
            self.post_calculation(expression)
        self.post_calculation("100 + 1", client_id="bob")
        response = self.client.get(reverse("api_history"), {"client_id": "alice"})
        self.assertEqual(
            [item["expression"] for item in response.json()],
            ["3 + 3", "2 + 2", "1 + 1"],
        )

    def test_clear_history_affects_one_client(self):
        self.post_calculation("2 + 2", client_id="alice")
        self.post_calculation("3 + 3", client_id="bob")
        response = self.client.delete(
            reverse("api_history"),
            data=json.dumps({"client_id": "alice"}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["deleted"], 1)
        self.assertFalse(Calculation.objects.filter(client_id="alice").exists())
        self.assertTrue(Calculation.objects.filter(client_id="bob").exists())

    def test_health_endpoint(self):
        response = self.client.get(reverse("api_health"))
        self.assertEqual(response.json(), {"service": "calculator", "status": "ok"})

    def test_wrong_http_methods_are_rejected(self):
        self.assertEqual(self.client.get(reverse("api_calculate")).status_code, 405)
        self.assertEqual(self.client.post(reverse("api_health")).status_code, 405)

