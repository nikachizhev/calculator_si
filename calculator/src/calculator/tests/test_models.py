from django.test import TestCase

from calculator.models import Calculation


class CalculationModelTests(TestCase):
    def test_string_representation(self):
        item = Calculation(expression="6 * 7", result="42", client_id="alice")
        self.assertEqual(str(item), "6 * 7 = 42")

    def test_default_order_is_newest_first(self):
        first = Calculation.objects.create(expression="1 + 1", result="2", client_id="alice")
        second = Calculation.objects.create(expression="2 + 2", result="4", client_id="alice")
        self.assertEqual(list(Calculation.objects.values_list("id", flat=True)), [second.id, first.id])

    def test_client_id_is_indexed(self):
        field = Calculation._meta.get_field("client_id")
        self.assertTrue(field.db_index)

