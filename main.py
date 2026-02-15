#!/usr/bin/env python3
"""
Carousell Marketplace CLI Application

Entry point for the marketplace command-line interface.
"""

import sys
from storage.repository import Repository
from parsers.command_parser import CommandParser
from commands.user_commands import UserCommand
from commands.listing_commands import ListingCommand
from commands.category_commands import CategoryCommand


def main():
    """Main application loop."""
    # Initialize repository
    storage = Repository()

    # Initialize command controllers
    user_cmd = UserCommand(storage)
    listing_cmd = ListingCommand(storage)
    category_cmd = CategoryCommand(storage)

    # Map commands to controller methods
    commands = {
        "REGISTER": user_cmd.register,
        "CREATE_LISTING": listing_cmd.create_listing,
        "DELETE_LISTING": listing_cmd.delete_listing,
        "GET_LISTING": listing_cmd.get_listing,
        "GET_CATEGORY": category_cmd.get_category,
        "GET_TOP_CATEGORY": category_cmd.get_top_category,
    }

    # Initialize parser
    parser = CommandParser()

    # Check if running interactively
    is_interactive = sys.stdin.isatty()
    prompt = "# " if is_interactive else ""

    # Main STDIN loop
    try:
        while True:
            # Display prompt and read input
            if is_interactive:
                line = input(prompt).strip()
            else:
                line = sys.stdin.readline()
                if not line:  # EOF
                    break
                line = line.strip()

            # Skip empty lines
            if not line:
                continue

            try:
                # Parse command
                cmd_name, args = parser.parse(line)

                # Check if command exists
                if cmd_name not in commands:
                    print(f"Error - unknown command '{cmd_name}'")
                    continue

                # Execute command method
                result = commands[cmd_name](*args)
                print(result)

            except ValueError as e:
                # Handle parsing errors (e.g., unclosed quotes)
                print(f"Error - {e}")

    except EOFError:
        # Handle Ctrl+D (EOF)
        sys.exit(0)

    except KeyboardInterrupt:
        # Handle Ctrl+C
        print()  # Print newline for clean exit
        sys.exit(0)


if __name__ == "__main__":
    main()
