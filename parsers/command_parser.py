import shlex
from typing import Tuple, List


class CommandParser:
    """Parses command-line input with support for quoted strings."""

    def parse(self, input_line: str) -> Tuple[str, List[str]]:
        """
        Parse a command line with quoted string support.

        Uses shlex for POSIX-compliant parsing:
        - Handles quotes: "multi word title"
        - Handles escaped quotes: "She said \\"hello\\""
        - Handles single and double quotes

        Returns:
            Tuple of (command_name, args_list)
        """
        try:
            tokens = shlex.split(input_line)
            if not tokens:
                return ("", [])

            command = tokens[0].upper()
            args = tokens[1:]
            return (command, args)

        except ValueError as e:
            # Handle unclosed quotes or other parsing errors
            raise ValueError(f"Invalid command format: {e}")
