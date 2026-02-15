from commands.base import Command
from models.category import Category
from models.user import User


class CategoryCommand(Command):
    """Handler for all category-related commands."""

    def get_category(self, *args) -> str:
        """
        Get all listings in a category with sorting.

        Args:
            args[0]: username (for authentication)
            args[1]: category
            args[2]: sort_type (sort_price or sort_time)
            args[3]: order (asc or dsc)

        Returns:
            Multi-line listing output or error message
        """
        if len(args) != 4:
            return "Error - invalid arguments"

        username, category_name, sort_type, order = args

        # Check if user exists using model method
        if not User.exists(username, self.storage):
            return "Error - unknown user"

        # Get category using model method
        category = Category.get_by_name(category_name, self.storage)
        if not category:
            return "Error - category not found"

        # Get listings using model method
        listings = category.get_listings(self.storage)

        if not listings:
            return "Error - category not found"

        # Sort based on parameters using model methods
        if sort_type == "sort_price":
            listings.sort(key=lambda x: x.get_sort_key_price())
        elif sort_type == "sort_time":
            listings.sort(key=lambda x: x.get_sort_key_time())
        else:
            return "Error - invalid sort type"

        # Apply order
        if order == "dsc":
            listings.reverse()
        elif order != "asc":
            return "Error - invalid sort order"

        # Format output (one listing per line)
        return "\n".join(listing.to_output_string() for listing in listings)

    def get_top_category(self, *args) -> str:
        """
        Get the category with the highest number of listings.

        Args:
            args[0]: username (for authentication)

        Returns:
            "<category>" or "Error - unknown user"
        """
        if len(args) != 1:
            return "Error - invalid arguments"

        username = args[0]

        # Check if user exists using model method
        if not User.exists(username, self.storage):
            return "Error - unknown user"

        # Call model method to get top category
        top_category = Category.get_top_category(self.storage)

        if not top_category:
            return "Error - no categories found"

        return top_category
