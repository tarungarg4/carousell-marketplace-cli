from typing import Optional, Dict
from models.user import User
from models.listing import Listing
from models.category import Category


class Repository:
    """Simple data repository - pure data storage with no business logic."""

    def __init__(self):
        # Simple storage dictionaries
        self.users: Dict[str, User] = {}  # key: username.lower()
        self.listings: Dict[int, Listing] = {}  # key: listing_id
        self.categories: Dict[str, Category] = {}  # key: category name

        # ID generation
        self.next_listing_id: int = 100001

    # User repository methods
    def save_user(self, user: User):
        """Save a user to storage."""
        self.users[user.username_key()] = user

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username (case-insensitive)."""
        return self.users.get(username.lower())

    def user_exists(self, username: str) -> bool:
        """Check if a user exists (case-insensitive)."""
        return username.lower() in self.users

    # Listing repository methods
    def save_listing(self, listing: Listing):
        """Save a listing to storage."""
        self.listings[listing.listing_id] = listing

    def get_listing(self, listing_id: int) -> Optional[Listing]:
        """Get a listing by ID."""
        return self.listings.get(listing_id)

    def delete_listing(self, listing_id: int):
        """Delete a listing from storage."""
        if listing_id in self.listings:
            del self.listings[listing_id]

    def get_next_listing_id(self) -> int:
        """Get the next listing ID and increment counter."""
        listing_id = self.next_listing_id
        self.next_listing_id += 1
        return listing_id

    # Category repository methods
    def save_category(self, category: Category):
        """Save a category to storage."""
        self.categories[category.name] = category

    def get_category(self, name: str) -> Optional[Category]:
        """Get a category by name."""
        return self.categories.get(name)

    def get_all_categories(self) -> Dict[str, Category]:
        """Get all categories."""
        return dict(self.categories)
