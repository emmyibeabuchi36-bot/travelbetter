import unittest
from currency_converter import convert_currency


class CurrencyConverterTests(unittest.TestCase):
    def test_same_currency(self):
        self.assertEqual(convert_currency(100, "USD", "USD"), 100)

    def test_usd_to_ngn(self):
        self.assertAlmostEqual(convert_currency(2, "USD", "NGN"), 3000)

    def test_unsupported_currency(self):
        with self.assertRaises(ValueError):
            convert_currency(10, "XYZ", "NGN")


if __name__ == "__main__":
    unittest.main()
