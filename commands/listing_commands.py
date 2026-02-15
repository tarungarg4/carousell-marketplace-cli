from commands.base import Command
from models.listing import Listing
from models.user import User


class ListingCommand(Command):
    """Handler for all listing-related commands."""

    def create_listing(self, *args) -> str:
        """
        Create a new listing.

        Args:
            args[0]: username
            args[1]: title
            args[2]: description
            args[3]: price
            args[4]: category

        Returns:
            "<listing_id>" or "Error - unknown user"
        """
        if len(args) != 5:
            return "Error - invalid arguments"

        username, title, description, price_str, category = args

        try:
            # Call model method which handles validation, business logic, and persistence
            listing = Listing.create(username, title, description, price_str, category, self.storage)
            return str(listing.listing_id)
        except ValueError as e:
            error_msg = str(e)
            # Return the error message as-is if it starts with "Error -"
            if error_msg.startswith("Error -"):
                return error_msg
            return f"Error - {e}"

    def get_listing(self, *args) -> str:
        """
        Get details of a listing.

        Args:
            args[0]: username (for authentication)
            args[1]: listing_id

        Returns:
            "<title>|<description>|<price>|<created_at>|<category>|<username>"
            or error message
        """
        if len(args) != 2:
            return "Error - invalid arguments"

        username, listing_id_str = args

        # Check if user exists using model method
        if not User.exists(username, self.storage):
            return "Error - unknown user"

        # Parse listing ID
        try:
            listing_id = int(listing_id_str)
        except ValueError:
            return "Error - invalid listing ID"

        # Get listing using model method
        listing = Listing.get_by_id(listing_id, self.storage)
        if not listing:
            return "Error - not found"

        return listing.to_output_string()

    def delete_listing(self, *args) -> str:
        """
        Delete a listing.

        Args:
            args[0]: username
            args[1]: listing_id

        Returns:
            "Success", "Error - listing does not exist", or "Error - listing owner mismatch"
        """
        if len(args) != 2:
            return "Error - invalid arguments"

        username, listing_id_str = args

        # Check if user exists using model method
        if not User.exists(username, self.storage):
            return "Error - unknown user"

        # Parse listing ID
        try:
            listing_id = int(listing_id_str)
        except ValueError:
            return "Error - invalid listing ID"

        # Get listing using model method
        listing = Listing.get_by_id(listing_id, self.storage)
        if not listing:
            return "Error - listing does not exist"

        # Validate ownership using model method
        if not listing.is_owned_by(username):
            return "Error - listing owner mismatch"

        # Delete listing using model method
        listing.delete(self.storage)
        return "Success"
