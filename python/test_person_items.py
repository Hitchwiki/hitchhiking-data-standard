import unittest

from hitchhiking_data_standard_pydantic_model import Hitchhiker, Occupant
from pydantic import ValidationError


class PersonItemsTest(unittest.TestCase):
    def test_hitchhiker_preserves_named_items_and_extra_attributes(self):
        person = Hitchhiker.model_validate(
            {
                "nickname": "Alice",
                "items": [
                    {"name": "dog"},
                    {"name": "bicycle", "folding": True},
                ],
            }
        )
        self.assertEqual(
            person.model_dump(exclude_none=True)["items"],
            [{"name": "dog"}, {"name": "bicycle", "folding": True}],
        )

    def test_items_are_available_to_any_person_subtype(self):
        occupant = Occupant.model_validate({"items": [{"name": "guitar"}]})
        self.assertEqual(occupant.items[0].name, "guitar")

    def test_existing_person_without_items_stays_valid(self):
        self.assertIsNone(Hitchhiker(nickname="Bob").items)

    def test_item_requires_a_nonempty_name(self):
        for item in ({}, {"name": ""}):
            with self.subTest(item=item), self.assertRaises(ValidationError):
                Hitchhiker.model_validate({"items": [item]})


if __name__ == "__main__":
    unittest.main()
