from commands.base import Command
from models.user import User


class UserCommand(Command):
    """Handler for all user-related commands."""

    def register(self, *args) -> str:
        """
        Register a new user.

        Args:
            args[0]: username

        Returns:
            "Success" or "Error - user already existing"
        """
        if len(args) != 1:
            return "Error - invalid arguments"

        username = args[0]

        try:
            # Call model method which handles business logic and persistence
            User.register(username, self.storage)
            return "Success"
        except ValueError as e:
            if "already exists" in str(e):
                return "Error - user already existing"
            return f"Error - {e}"
