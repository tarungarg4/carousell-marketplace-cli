from dataclasses import dataclass, field
from typing import Set, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from storage.repository import Repository
    from models.listing import Listing


@dataclass
class Category:
    """Represents a category in the marketplace with business logic."""
    name: str
    listing_ids: Set[int] = field(default_factory=set)

    def add_listing(self, listing_id: int):
        """Add a listing to this category."""
        self.listing_ids.add(listing_id)

    def remove_listing(self, listing_id: int):
        """Remove a listing from this category."""
        self.listing_ids.discard(listing_id)

    def get_listing_count(self) -> int:
        """Get the number of listings in this category."""
        return len(self.listing_ids)

    def has_listings(self) -> bool:
        """Check if this category has any listings."""
        return len(self.listing_ids) > 0

    @staticmethod
    def get_by_name(name: str, repo: 'Repository') -> Optional['Category']:
        """
        Get a category by name.

        Args:
            name: Category name
            repo: Repository to query

        Returns:
            Category or None
        """
        return repo.get_category(name)

    def get_listings(self, repo: 'Repository') -> List['Listing']:
        """
        Get all listings in this category.

        Args:
            repo: Repository to fetch listings from

        Returns:
            List of Listing objects
        """
        listings = []
        for listing_id in self.listing_ids:
            listing = repo.get_listing(listing_id)
            if listing:
                listings.append(listing)
        return listings

    @staticmethod
    def get_top_category(repo: 'Repository') -> Optional[str]:
        """
        Get the category with the most listings.

        Args:
            repo: Repository to get categories from

        Returns:
            Category name or None
        """
        categories = repo.get_all_categories()
        if not categories:
            return None

        # Filter categories that have listings
        categories_with_listings = [(name, cat.get_listing_count())
                                    for name, cat in categories.items()
                                    if cat.has_listings()]

        if not categories_with_listings:
            return None

        # Use count as primary key, category name (alphabetically later) as tiebreaker
        return max(categories_with_listings, key=lambda x: (x[1], x[0]))[0]
