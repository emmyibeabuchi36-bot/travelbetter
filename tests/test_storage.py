import tempfile
import unittest
from pathlib import Path
from budget import TravelBudget
from expenses import add_expense
from storage import save_trip, load_trip


class StorageTests(unittest.TestCase):
    def test_save_and_load_trip(self):
        trip = TravelBudget("Accra trip", "GHS", 5000)
        add_expense(trip, "food", "Lunch", 50)
        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / "trip.json"
            save_trip(trip, file_path)
            restored = load_trip(file_path)
        self.assertEqual(restored.name, trip.name)
        self.assertEqual(restored.total_spent, 50)


if __name__ == "__main__":
    unittest.main()
