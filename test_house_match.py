import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from Tati.HouseMatch import (
    DatasetError,
    FeatureSpace,
    RecommendationEngine,
    listing_details,
    load_listings,
)


class HouseMatchTests(unittest.TestCase):
    def test_load_listings_reads_nested_sample_without_extracting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "dataset.zip"
            payload = {
                "house-a": listing(price=100_000, images=["https://example/a.jpg"]),
                "house-b": listing(price=200_000, images=[]),
            }
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("nested/dataset_sample.json", json.dumps(payload))

            loaded = load_listings(archive)

            self.assertEqual([house.listing_id for house in loaded], ["house-a", "house-b"])
            self.assertEqual(loaded[0].images, ("https://example/a.jpg",))
            self.assertEqual(
                sorted(path.name for path in root.iterdir()), ["dataset.zip"]
            )

    def test_load_listings_rejects_archive_without_sample(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "dataset.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("full.json", "{}")

            with self.assertRaisesRegex(DatasetError, "sample JSON"):
                load_listings(archive)

    def test_load_listings_rejects_corrupt_required_values(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "dataset.zip"
            payload = {"house-a": listing(price="not-a-number")}
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("nested/dataset_sample.json", json.dumps(payload))

            with self.assertRaisesRegex(DatasetError, "house-a.*price"):
                load_listings(archive)

    def test_feature_space_normalizes_numbers_and_imputes_missing_values(self):
        houses = [
            make_house("low", price=100.0, square_meters=50.0),
            make_house("missing", price=None, square_meters=75.0),
            make_house("high", price=300.0, square_meters=100.0),
        ]

        features = FeatureSpace(houses)

        self.assertEqual(features.for_listing("low").numeric[0], 0.0)
        self.assertEqual(features.for_listing("high").numeric[0], 1.0)
        self.assertEqual(features.for_listing("missing").numeric[0], 0.5)
        self.assertEqual(features.for_listing("missing").numeric[1], 0.5)

    def test_listing_details_handles_missing_numerical_values(self):
        house = make_house("sparse", price=None, square_meters=None)
        house = type(house)(
            **{
                **house.__dict__,
                "bedrooms": None,
                "bathrooms": None,
            }
        )

        details = listing_details(house)

        self.assertIn("Unknown price", details)
        self.assertIn("Unknown m2", details)
        self.assertIn("Unknown bedrooms", details)
        self.assertIn("Unknown bathrooms", details)

    def test_vote_updates_preference_and_advances_to_unseen_pair(self):
        houses = [
            make_house(
                f"house-{index}",
                price=float(index * 100),
                city="Barcelona" if index < 3 else "Girona",
            )
            for index in range(6)
        ]
        engine = RecommendationEngine(houses, seed=7)
        first_pair = engine.current_pair
        chosen = first_pair[0]
        before = engine.preference_revision

        second_pair = engine.vote(0)

        self.assertEqual(engine.preference_revision, before + 1)
        self.assertEqual(engine.vote_history, (chosen.listing_id,))
        self.assertEqual(len({house.listing_id for house in second_pair}), 2)
        self.assertTrue(
            {house.listing_id for house in first_pair}.isdisjoint(
                house.listing_id for house in second_pair
            )
        )
        ranked_ids = [house.listing_id for house in engine.ranked_listings()]
        self.assertEqual(ranked_ids[0], chosen.listing_id)

    def test_consecutive_votes_never_show_identical_houses(self):
        houses = [make_house(f"house-{index}", price=float(index)) for index in range(8)]
        engine = RecommendationEngine(houses, seed=3)

        seen_pairs = set()
        for _ in range(6):
            pair = engine.current_pair
            pair_ids = tuple(house.listing_id for house in pair)
            self.assertNotEqual(pair_ids[0], pair_ids[1])
            self.assertNotIn(frozenset(pair_ids), seen_pairs)
            seen_pairs.add(frozenset(pair_ids))
            engine.vote(0)


def listing(price=150_000, images=None):
    return {
        "city": "Barcelona",
        "neighborhood": "Eixample",
        "region": "barcelones",
        "price": price,
        "square_meters": 80,
        "bedrooms": 2,
        "bathrooms": 1,
        "property_type": "condo_apartment",
        "images": [] if images is None else images,
        "image_data": {
            "style": {"label": "modern"},
            "r1r6": {
                "property": 4,
                "kitchen": 3,
                "bathroom": 2,
                "interior": 5,
            },
        },
    }


def make_house(listing_id, price, square_meters=80.0, city="Barcelona"):
    from Tati.HouseMatch import Listing

    return Listing(
        listing_id=listing_id,
        city=city,
        neighborhood="Eixample",
        region="barcelones",
        style="modern",
        property_type="condo_apartment",
        price=price,
        square_meters=square_meters,
        bedrooms=2.0,
        bathrooms=1.0,
        visual_property=4.0,
        visual_kitchen=3.0,
        visual_bathroom=2.0,
        visual_interior=5.0,
        images=(f"https://example/{listing_id}.jpg",),
    )


if __name__ == "__main__":
    unittest.main()