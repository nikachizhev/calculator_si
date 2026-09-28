from django.test import SimpleTestCase

from calculator.services.evaluator import CalculationError, calculate


class EvaluatorSecurityTests(SimpleTestCase):
    def test_python_constructs_are_rejected(self):
        expressions = (
            "__import__('os')",
            "open('secret.txt')",
            "(1).__class__",
            "[1, 2, 3]",
            "{'value': 1}",
            "lambda: 1",
            "True",
            "None",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    calculate(expression)

    def test_invalid_call_shapes_are_rejected(self):
        for expression in ("sqrt()", "sqrt(4, 9)", "sqrt(x=4)", "math.sqrt(4)", "pi()"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    calculate(expression)

    def test_resource_limits(self):
        for expression in ("factorial(101)", "10 ^ 1000", "9" * 201):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    calculate(expression)

    def test_empty_and_broken_expressions(self):
        for expression in ("", "   ", "(2 + 3", "2 +"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    calculate(expression)

