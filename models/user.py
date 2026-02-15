from dataclasses import dataclass, field
from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from storage.repository import Repository


@dataclass
class User:
    """Represents a user aggregate in the marketplace with business logic."""
    username: str  # Original casing preserved
    listing_ids: Set[int] = field(default_factory=set)

    def username_key(self) -> str:
        """Returns normalized username for case-insensitive lookups."""
        return self.username.lower()

    def add_listing(self, listing_id: int):
        """Add a listing created by this user."""
        self.listing_ids.add(listing_id)

    def remove_listing(self, listing_id: int):
        """Remove a listing from this user."""
        self.listing_ids.discard(listing_id)

    @staticmethod
    def exists(username: str, repo: 'Repository') -> bool:
        """
        Check if a user exists.

        Args:
            username: Username to check
            repo: Repository to query

        Returns:
            True if user exists, False otherwise
        """
        return repo.user_exists(username)

    @staticmethod
    def register(username: str, repo: 'Repository') -> 'User':
        """
        Register a new user (factory method with repository access).

        Args:
            username: The username to register
            repo: Repository for persistence

        Returns:
            The newly created User

        Raises:
            ValueError: If user already exists
        """
        if User.exists(username, repo):
            raise ValueError("User already exists")

        user = User(username=username)
        repo.save_user(user)
        return user
