import unittest

from pydantic import ValidationError

from hitchhiking_data_standard_pydantic_model import HitchhikingRecord


def record(**updates):
    value = {
        "version": "0.0.0",
        "stops": [
            {
                "location": {
                    "latitude": 52.3020268,
                    "longitude": 13.0158591,
                    "is_exact": True,
                }
            }
        ],
        "hitchhikers": [{"nickname": "Anonymous"}],
        "source": "private",
        "license": "odbl",
        "submission_time": "2026-08-19T12:00:00+02:00[Europe/Berlin]",
    }
    value.update(updates)
    return value


class PaymentDemandedTest(unittest.TestCase):
    def test_expected_payment_is_valid_on_a_ride(self):
        parsed = HitchhikingRecord.model_validate(
            record(ride={"expected_payment": (10, "EUR")})
        )
        self.assertEqual(parsed.ride.expected_payment, (10, "EUR"))

    def test_existing_ride_without_expected_payment_remains_valid(self):
        parsed = HitchhikingRecord.model_validate(
            record(ride={"reasons": ["commute"]})
        )
        self.assertIsNone(parsed.ride.expected_payment)

    def test_payment_demanded_is_valid_declined_ride_reason(self):
        parsed = HitchhikingRecord.model_validate(
            record(
                declined_rides=[
                    {
                        "reasons": ["payment_demanded"],
                        "expected_payment": (10000, "SATS"),
                    }
                ]
            )
        )
        self.assertEqual(parsed.declined_rides[0].reasons, ["payment_demanded"])
        self.assertEqual(parsed.declined_rides[0].expected_payment, (10000, "SATS"))

    def test_unknown_declined_ride_reason_is_rejected(self):
        with self.assertRaises(ValidationError):
            HitchhikingRecord.model_validate(
                record(declined_rides=[{"reasons": ["asked_for_money"]}])
            )


if __name__ == "__main__":
    unittest.main()
