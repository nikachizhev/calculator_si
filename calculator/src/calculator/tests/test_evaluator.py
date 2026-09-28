import math

from django.test import SimpleTestCase

from calculator.services.evaluator import CalculationError, calculate


class EvaluatorTests(SimpleTestCase):
    def test_basic_arithmetic(self):
        cases = {
            "2 + 3 * 4": 14,
            "(2.5 + 1.5) / 2": 2,
            "17 % 5": 2,
            "-7 + 2": -5,
            "3 ^ 4": 81,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(calculate(expression), expected)

    def test_scientific_functions(self):
        cases = {
            "sqrt(81)": 9,
            "log(1000)": 3,
            "ln(e)": 1,
            "sin(pi / 2)": 1,
            "cos(0)": 1,
            "tan(pi / 4)": 1,
            "abs(-12)": 12,
            "factorial(6)": 720,
            "asin(1)": math.pi / 2,
            "acos(1)": 0,
            "atan(1)": math.pi / 4,
            "exp(1)": math.e,
            "floor(2.9)": 2,
            "ceil(2.1)": 3,
            "degrees(pi)": 180,
            "radians(180)": math.pi,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertAlmostEqual(calculate(expression), expected)

    def test_constants(self):
        self.assertAlmostEqual(calculate("pi"), math.pi)
        self.assertAlmostEqual(calculate("e"), math.e)

    def test_complex_expression_from_specification(self):
        result = calculate("(12 + 22*7) / (33 + (12*3 - 8)) * 3")
        self.assertAlmostEqual(result, 8.163934426229508)

    def test_domain_errors(self):
        for expression in ("1 / 0", "sqrt(-1)", "log(0)", "factorial(2.5)"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    calculate(expression)

