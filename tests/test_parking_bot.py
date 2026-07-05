import unittest

from parking_bot import parse_slot_number, pick_first_available_slot_text


class ParkingBotHelpersTests(unittest.TestCase):
    def test_parse_slot_number_in_range(self):
        self.assertEqual(parse_slot_number("Slot 304 - Available"), 304)

    def test_parse_slot_number_missing(self):
        self.assertIsNone(parse_slot_number("Slot 401 - Available"))

    def test_pick_first_available_slot(self):
        rows = [
            "301 4-wheeler Booked",
            "302 4-wheeler Available",
            "304 4-wheeler Available",
        ]
        self.assertEqual(pick_first_available_slot_text(rows), "302 4-wheeler Available")

    def test_pick_first_available_slot_none(self):
        rows = [
            "301 4-wheeler Booked",
            "302 4-wheeler Booked",
        ]
        self.assertIsNone(pick_first_available_slot_text(rows))


if __name__ == "__main__":
    unittest.main()
