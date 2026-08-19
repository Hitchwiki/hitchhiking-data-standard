import unittest

from hitchhiking_data_standard_pydantic_model import Gift, Ride
from pydantic import ValidationError


class PriceShapeTest(unittest.TestCase):
    def test_decimal_strings_survive_without_changing_json_type(self):
        gift = Gift(kind="money", price=("10.50", "EUR"))
        ride = Ride(expected_payment=("10000", "SATS"))
        self.assertEqual(gift.model_dump()["price"], ("10.50", "EUR"))
        self.assertEqual(ride.model_dump()["expected_payment"], ("10000", "SATS"))

    def test_numeric_or_invalid_amount_does_not_violate_json_schema_shape(self):
        for amount in (10, 0.5, "-1", "1e3", ""):
            with self.subTest(amount=amount), self.assertRaises(ValidationError):
                Gift(kind="money", price=(amount, "EUR"))


if __name__ == "__main__":
    unittest.main()
