"""Pure recommendation core for the house-preference demo."""

from __future__ import annotations

import json
import math
import random
import statistics
import zipfile
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Mapping, Sequence


DEFAULT_ARCHIVE = (
    Path(__file__).resolve().parents[1]
    / "restbai"
    / "hackupc2023_restbai__dataset.zip"
)
SAMPLE_SUFFIX = "_sample.json"
CATEGORICAL_ATTRIBUTES = (
    "city",
    "neighborhood",
    "region",
    "style",
    "property_type",
)
NUMERICAL_ATTRIBUTES = (
    "price",
    "square_meters",
    "bedrooms",
    "bathrooms",
    "visual_property",
    "visual_kitchen",
    "visual_bathroom",
    "visual_interior",
)


class DatasetError(ValueError):
    """Raised when the bundled listing sample cannot be loaded safely."""


@dataclass(frozen=True)
class Listing:
    listing_id: str
    city: str
    neighborhood: str
    region: str
    style: str
    property_type: str
    price: float | None
    square_meters: float | None
    bedrooms: float | None
    bathrooms: float | None
    visual_property: float | None
    visual_kitchen: float | None
    visual_bathroom: float | None
    visual_interior: float | None
    images: tuple[str, ...]


@dataclass(frozen=True)
class FeatureVector:
    categorical: tuple[str, ...]
    numeric: tuple[float, ...]


def _text(value: object) -> str:
    if value is None:
        return "Unknown"
    normalized = str(value).strip()
    return normalized or "Unknown"


def _number(value: object, listing_id: str, field_name: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise DatasetError(
            f"listing {listing_id!r} has invalid {field_name}: {value!r}"
        ) from error
    if not math.isfinite(number):
        raise DatasetError(
            f"listing {listing_id!r} has invalid {field_name}: {value!r}"
        )
    return number


def _listing_from_payload(listing_id: object, payload: object) -> Listing:
    identifier = str(listing_id).strip()
    if not identifier:
        raise DatasetError("sample contains a blank listing identifier")
    if not isinstance(payload, Mapping):
        raise DatasetError(f"listing {identifier!r} is not a JSON object")

    image_data = payload.get("image_data")
    image_data = image_data if isinstance(image_data, Mapping) else {}
    style_data = image_data.get("style")
    style_data = style_data if isinstance(style_data, Mapping) else {}
    visual_data = image_data.get("r1r6")
    visual_data = visual_data if isinstance(visual_data, Mapping) else {}
    raw_images = payload.get("images")
    if raw_images is None:
        raw_images = []
    if not isinstance(raw_images, list):
        raise DatasetError(f"listing {identifier!r} has invalid images: expected a list")
    images = tuple(str(url).strip() for url in raw_images if str(url).strip())

    return Listing(
        listing_id=identifier,
        city=_text(payload.get("city")),
        neighborhood=_text(payload.get("neighborhood")),
        region=_text(payload.get("region")),
        style=_text(style_data.get("label")),
        property_type=_text(payload.get("property_type")),
        price=_number(payload.get("price"), identifier, "price"),
        square_meters=_number(
            payload.get("square_meters"), identifier, "square_meters"
        ),
        bedrooms=_number(payload.get("bedrooms"), identifier, "bedrooms"),
        bathrooms=_number(payload.get("bathrooms"), identifier, "bathrooms"),
        visual_property=_number(
            visual_data.get("property"), identifier, "visual property score"
        ),
        visual_kitchen=_number(
            visual_data.get("kitchen"), identifier, "visual kitchen score"
        ),
        visual_bathroom=_number(
            visual_data.get("bathroom"), identifier, "visual bathroom score"
        ),
        visual_interior=_number(
            visual_data.get("interior"), identifier, "visual interior score"
        ),
        images=images,
    )


def load_listings(archive_path: Path | str = DEFAULT_ARCHIVE) -> list[Listing]:
    """Load only the nested sample JSON directly from the tracked ZIP archive."""
    path = Path(archive_path)
    try:
        archive = zipfile.ZipFile(path)
    except FileNotFoundError as error:
        raise DatasetError(
            f"dataset archive not found at {path}; restore the tracked ZIP file"
        ) from error
    except (OSError, zipfile.BadZipFile) as error:
        raise DatasetError(f"cannot read sample data from {path}: {error}") from error

    try:
        with archive:
            sample_members = sorted(
                name for name in archive.namelist() if name.endswith(SAMPLE_SUFFIX)
            )
            if not sample_members:
                raise DatasetError(f"archive {path} contains no sample JSON member")
            if len(sample_members) > 1:
                raise DatasetError(f"archive {path} contains multiple sample JSON members")
            with archive.open(sample_members[0]) as sample_file:
                payload = json.load(sample_file)
    except (OSError, json.JSONDecodeError) as error:
        raise DatasetError(f"cannot read sample data from {path}: {error}") from error

    if not isinstance(payload, dict) or not payload:
        raise DatasetError("sample JSON must be a non-empty object keyed by listing ID")
    listings = [
        _listing_from_payload(listing_id, listing_payload)
        for listing_id, listing_payload in sorted(
            payload.items(), key=lambda item: str(item[0])
        )
    ]
    if len({listing.listing_id for listing in listings}) != len(listings):
        raise DatasetError("sample contains duplicate listing identifiers")
    return listings


class FeatureSpace:
    """Median-impute and normalize listing features for mixed-distance ranking."""

    def __init__(self, listings: Sequence[Listing]):
        if not listings:
            raise ValueError("at least one listing is required")
        self._listings = {listing.listing_id: listing for listing in listings}
        if len(self._listings) != len(listings):
            raise ValueError("listing identifiers must be unique")

        self._medians = []
        self._ranges = []
        for attribute in NUMERICAL_ATTRIBUTES:
            available = [
                value
                for listing in listings
                if (value := getattr(listing, attribute)) is not None
            ]
            median = statistics.median(available) if available else 0.0
            imputed = [
                median
                if getattr(listing, attribute) is None
                else getattr(listing, attribute)
                for listing in listings
            ]
            self._medians.append(float(median))
            self._ranges.append((float(min(imputed)), float(max(imputed))))

        self._vectors = {
            listing.listing_id: self._build_vector(listing) for listing in listings
        }

    def _build_vector(self, listing: Listing) -> FeatureVector:
        categorical = tuple(
            _text(getattr(listing, attribute)).casefold()
            for attribute in CATEGORICAL_ATTRIBUTES
        )
        numeric = []
        for index, attribute in enumerate(NUMERICAL_ATTRIBUTES):
            raw_value = getattr(listing, attribute)
            value = self._medians[index] if raw_value is None else float(raw_value)
            minimum, maximum = self._ranges[index]
            numeric.append(
                0.5 if maximum == minimum else (value - minimum) / (maximum - minimum)
            )
        return FeatureVector(categorical=categorical, numeric=tuple(numeric))

    def for_listing(self, listing: Listing | str) -> FeatureVector:
        identifier = listing if isinstance(listing, str) else listing.listing_id
        try:
            return self._vectors[identifier]
        except KeyError as error:
            raise KeyError(f"unknown listing ID: {identifier}") from error


def mixed_distance(left: FeatureVector, right: FeatureVector) -> float:
    """Return equal-weight Gower-style distance over categorical and numeric features."""
    categorical_distance = [
        float(left_value != right_value)
        for left_value, right_value in zip(
            left.categorical, right.categorical, strict=True
        )
    ]
    numerical_distance = [
        abs(left_value - right_value)
        for left_value, right_value in zip(left.numeric, right.numeric, strict=True)
    ]
    distances = categorical_distance + numerical_distance
    return sum(distances) / len(distances)


def listing_details(listing: Listing) -> str:
    def measurement(value: float | None, unit: str) -> str:
        return f"Unknown {unit}" if value is None else f"{value:g} {unit}"

    price = "Unknown price" if listing.price is None else f"EUR {listing.price:,.0f}"
    return (
        f"{listing.city} - {listing.neighborhood}\n"
        f"{price} | {measurement(listing.square_meters, 'm2')} | "
        f"{measurement(listing.bedrooms, 'bedrooms')} | "
        f"{measurement(listing.bathrooms, 'bathrooms')}\n"
        f"{listing.property_type.replace('_', ' ')} | {listing.style}"
    )


class RecommendationEngine:
    """Maintain a vote-derived preference profile and non-repeating house pairs."""

    def __init__(self, listings: Sequence[Listing], seed: int = 2023):
        if len(listings) < 4:
            raise ValueError("at least four listings are required for pair progression")
        self.listings = tuple(listings)
        self.features = FeatureSpace(self.listings)
        self._random = random.Random(seed)
        self._preference: FeatureVector | None = None
        self._categorical_votes: list[tuple[str, ...]] = []
        self._numeric_total = [0.0] * len(NUMERICAL_ATTRIBUTES)
        self._vote_history: list[str] = []
        self.preference_revision = 0

        initial_pair = tuple(self._random.sample(self.listings, 2))
        self.current_pair: tuple[Listing, Listing] = (
            initial_pair[0],
            initial_pair[1],
        )
        self._pair_history = {
            frozenset(listing.listing_id for listing in self.current_pair)
        }

    @property
    def vote_history(self) -> tuple[str, ...]:
        return tuple(self._vote_history)

    def vote(self, side: int) -> tuple[Listing, Listing]:
        if side not in (0, 1):
            raise ValueError("side must be 0 or 1")
        chosen = self.current_pair[side]
        chosen_features = self.features.for_listing(chosen)
        self._vote_history.append(chosen.listing_id)
        self._categorical_votes.append(chosen_features.categorical)
        for index, value in enumerate(chosen_features.numeric):
            self._numeric_total[index] += value
        self.preference_revision += 1
        self._preference = FeatureVector(
            categorical=tuple(
                Counter(vote[index] for vote in self._categorical_votes)
                .most_common(1)[0][0]
                for index in range(len(CATEGORICAL_ATTRIBUTES))
            ),
            numeric=tuple(
                total / self.preference_revision for total in self._numeric_total
            ),
        )
        self.current_pair = self._next_pair()
        return self.current_pair

    def ranked_listings(self) -> list[Listing]:
        if self._preference is None:
            return sorted(self.listings, key=lambda listing: listing.listing_id)
        return sorted(
            self.listings,
            key=lambda listing: (
                mixed_distance(self._preference, self.features.for_listing(listing)),
                listing.listing_id,
            ),
        )

    def _next_pair(self) -> tuple[Listing, Listing]:
        previous_ids = {listing.listing_id for listing in self.current_pair}
        ranked = self.ranked_listings()
        candidates = [
            listing for listing in ranked if listing.listing_id not in previous_ids
        ]
        if len(candidates) < 2:
            candidates = ranked

        pair = self._first_unused_pair(candidates)
        if pair is None:
            pair = self._first_unused_pair(ranked)
        if pair is None:
            raise RuntimeError("all possible listing pairs have already been shown")
        self._pair_history.add(frozenset(listing.listing_id for listing in pair))
        return pair

    def _first_unused_pair(
        self, candidates: Sequence[Listing]
    ) -> tuple[Listing, Listing] | None:
        for left, right in combinations(candidates, 2):
            pair_id = frozenset((left.listing_id, right.listing_id))
            if pair_id not in self._pair_history:
                return left, right
        return None