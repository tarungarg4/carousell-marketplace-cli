# Carousell Marketplace CLI

A command-line marketplace platform that allows users to register, create listings, and browse items by category.

## Features

- User registration with case-insensitive usernames
- Create, read, and delete listings
- Category-based browsing with sorting (by price or time, ascending or descending)
- Top category retrieval with alphabetical tiebreaker
- Auto-incrementing listing IDs starting at 100001

## Requirements

- **Python 3.x** (Python 3.5+ supported; the default `python2.7` on Debian 9 will NOT work)
- No external libraries — uses only the Python standard library

To install Python 3 on Debian 9:

```bash
sudo apt-get update && sudo apt-get install -y python3
```

## Build & Run

```bash
./build.sh          # No build step needed for Python
./run.sh             # Starts the interactive CLI (reads from stdin)
./run.sh < input.txt # Batch mode
```

Or directly:

```bash
python3 main.py
python3 main.py < input.txt
```

## Available Commands

### REGISTER

Register a new user.

```
REGISTER <username>
```

**Responses:**
- `Success` - User registered successfully
- `Error - user already existing` - Username already taken

### CREATE_LISTING

Create a new listing for an item.

```
CREATE_LISTING <username> <title> <description> <price> <category>
```

**Note:** Use quotes for multi-word titles, descriptions, or categories.

**Responses:**
- `<listing_id>` - Listing created successfully (returns the listing ID)
- `Error - unknown user` - User does not exist
- `Error - invalid price` - Price is not a valid number or is negative

### GET_LISTING

Get details of a specific listing.

```
GET_LISTING <username> <listing_id>
```

**Responses:**
- `<title>|<description>|<price>|<created_at>|<category>|<username>` - Listing details
- `Error - not found` - Listing does not exist
- `Error - unknown user` - User does not exist

### DELETE_LISTING

Delete a listing (must be the owner).

```
DELETE_LISTING <username> <listing_id>
```

**Responses:**
- `Success` - Listing deleted successfully
- `Error - listing does not exist` - Listing not found
- `Error - listing owner mismatch` - User is not the owner

### GET_CATEGORY

Get all listings in a category with sorting.

```
GET_CATEGORY <username> <category> {sort_price|sort_time} {asc|dsc}
```

**Sort Options:**
- `sort_price` / `sort_time` - Sort field
- `asc` / `dsc` - Sort order

**Responses:**
- Multi-line output with one listing per line (same format as GET_LISTING)
- `Error - category not found` - No listings in category
- `Error - unknown user` - User does not exist

### GET_TOP_CATEGORY

Get the category with the most listings.

```
GET_TOP_CATEGORY <username>
```

**Responses:**
- `<category>` - Name of the top category
- `Error - unknown user` - User does not exist

**Note:** When multiple categories have the same count, the one that is later alphabetically is returned.

## Example Session

```
# REGISTER user1
Success
# CREATE_LISTING user1 'Phone model 8' 'Black color, brand new' 1000 'Electronics'
100001
# GET_LISTING user1 100001
Phone model 8|Black color, brand new|1000|2026-02-11 12:34:56|Electronics|user1
# CREATE_LISTING user1 'Black shoes' 'Training shoes' 100 'Sports'
100002
# GET_CATEGORY user1 'Sports' sort_price asc
Black shoes|Training shoes|100|2026-02-11 12:34:57|Sports|user1
# GET_TOP_CATEGORY user1
Electronics
# DELETE_LISTING user1 100001
Success
```

## Architecture

The application follows a **layered architecture** with one-way dependencies:

```
Commands (Application Layer)  -->  Models (Domain Layer)  -->  Repository (Data Layer)
```

- **commands/** - Application layer that handles user input and calls model methods
- **models/** - Rich domain models (User, Listing, Category) with business logic
- **storage/** - Repository providing pure CRUD data access
- **parsers/** - Command-line parsing with quoted string support
- **main.py** - Application entry point and STDIN loop

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

## Testing

```bash
python3 main.py < test_input.txt
```

Compare with expected output:

```bash
python3 main.py < test_input.txt > actual_output.txt
diff expected_output.txt actual_output.txt
```
