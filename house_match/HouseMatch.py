"""Compatibility imports for the restored recommendation core."""

from house_match.recommender import (
    DatasetError,
    FeatureSpace,
    FeatureVector,
    Listing,
    RecommendationEngine,
    listing_details,
    load_listings,
    mixed_distance,
)

__all__ = [
    "DatasetError",
    "FeatureSpace",
    "FeatureVector",
    "Listing",
    "RecommendationEngine",
    "listing_details",
    "load_listings",
    "mixed_distance",
]
