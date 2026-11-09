import unittest
from budget import TravelBudget
from expenses import add_expense, expense_summary


class BudgetExpenseTests(unittest.TestCase):
    def setUp(self):
        self.trip = TravelBudget("Lagos weekend", "NGN", 100000)

    def test_add_expense_and_remaining(self):
        add_expense(self.trip, "food", "Dinner", 12000)
        self.assertEqual(self.trip.remaining, 88000)

    def test_over_budget_status(self):
        add_expense(self.trip, "transport", "Flight", 120000)
        self.assertEqual(expense_summary(self.trip)["status"], "Over budget")

    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            add_expense(self.trip, "shopping-ish", "Item", 1000)


if __name__ == "__main__":
    unittest.main()
