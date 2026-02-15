from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from storage.repository import Repository


@dataclass
class Listing:
    """Represents a listing in the marketplace with business logic."""
    listing_id: int
    username: str
    title: str
    description: str
    price: float
    category: str
    creation_time: datetime

    @staticmethod
    def create(username: str, title: str, description: str,
               price: float, category: str, repo: 'Repository') -> 'Listing':
        """
        Create a new listing with validation and persist to repository.

        Args:
            username: Owner username
            title: Listing title
            description: Listing description
            price: Listing price
            category: Listing category
            repo: Repository for persistence

        Returns:
            The newly created Listing

        Raises:
            ValueError: If price is invalid or user doesn't exist
        """
        # Validate price
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise ValueError("Error - invalid price")
        if price_float < 0:
            raise ValueError("Error - invalid price")

        # Check if user exists
        user = repo.get_user(username)
        if not user:
            raise ValueError("Error - unknown user")

        # Get listing ID
        listing_id = repo.get_next_listing_id()

        # Create listing
        listing = Listing(
            listing_id=listing_id,
            username=username,
            title=title,
            description=description,
            price=price_float,
            category=category,
            creation_time=datetime.now()
        )

        # Save to repository
        repo.save_listing(listing)

        # Update user aggregate
        user.add_listing(listing_id)
        repo.save_user(user)

        # Update category aggregate
        from models.category import Category
        category_obj = repo.get_category(category)
        if not category_obj:
            category_obj = Category(name=category)
        category_obj.add_listing(listing_id)
        repo.save_category(category_obj)

        return listing

    @staticmethod
    def get_by_id(listing_id: int, repo: 'Repository') -> Optional['Listing']:
        """
        Get a listing by ID.

        Args:
            listing_id: Listing ID to retrieve
            repo: Repository to query

        Returns:
            Listing or None
        """
        return repo.get_listing(listing_id)

    def delete(self, repo: 'Repository') -> bool:
        """
        Delete this listing and update all aggregates.

        Args:
            repo: Repository for persistence

        Returns:
            True if successful
        """
        # Update user aggregate
        user = repo.get_user(self.username)
        if user:
            user.remove_listing(self.listing_id)
            repo.save_user(user)

        # Update category aggregate
        category = repo.get_category(self.category)
        if category:
            category.remove_listing(self.listing_id)
            repo.save_category(category)

        # Delete from repository
        repo.delete_listing(self.listing_id)

        return True

    def is_owned_by(self, username: str) -> bool:
        """Check if this listing belongs to the given user (case-insensitive)."""
        return self.username.lower() == username.lower()

    def get_sort_key_price(self) -> float:
        """Get the sort key for price-based sorting."""
        return self.price

    def get_sort_key_time(self) -> datetime:
        """Get the sort key for time-based sorting."""
        return self.creation_time

    def format_time(self) -> str:
        """Returns formatted timestamp in YYYY-MM-DD HH:MM:SS format."""
        return self.creation_time.strftime("%Y-%m-%d %H:%M:%S")

    def to_output_string(self) -> str:
        """Returns the listing formatted for output."""
        return f"{self.title}|{self.description}|{int(self.price)}|{self.format_time()}|{self.category}|{self.username}"
