# Architecture: Layered Domain-Driven Design

## Overview

This application follows a **layered architecture** where dependencies flow in one direction:

```
┌─────────────────────────────────────┐
│   Commands (Application Layer)      │
│   - Parse user input                │
│   - Call model methods              │
│   - Format responses                │
│   - NO direct repository access     │
└──────────────┬──────────────────────┘
               │ calls
               ▼
┌─────────────────────────────────────┐
│   Models (Domain Layer)             │
│   - Business logic & validation     │
│   - Aggregate management            │
│   - Call repository for persistence │
└──────────────┬──────────────────────┘
               │ calls
               ▼
┌─────────────────────────────────────┐
│   Repository (Data Layer)           │
│   - Simple CRUD operations          │
│   - NO business logic               │
│   - Just storage                    │
└─────────────────────────────────────┘
```

---

## Layer 1: Repository (Data Layer)

**File**: `storage/repository.py`

**Purpose**: Pure data storage with no business logic.

### Methods:
```python
# User operations
save_user(user: User)
get_user(username: str) -> Optional[User]
user_exists(username: str) -> bool

# Listing operations
save_listing(listing: Listing)
get_listing(listing_id: int) -> Optional[Listing]
delete_listing(listing_id: int)
get_next_listing_id() -> int

# Category operations
save_category(category: Category)
get_category(name: str) -> Optional[Category]
get_all_categories() -> Dict[str, Category]
```

**Key Principle**: Repository is a "dumb" storage layer - it just saves and retrieves objects without understanding business rules.

---

## Layer 2: Models (Domain Layer)

**Files**: `models/user.py`, `models/listing.py`, `models/category.py`

**Purpose**: Rich domain objects with business logic that use the repository.

### User Model

**Data**: `username`, `listing_ids` (set)

**Instance Methods**:
- `username_key()` - Case-insensitive lookup key
- `add_listing(listing_id)` / `remove_listing(listing_id)` - Manage user's listings

**Static Methods** (call repository):
- `User.exists(username, repo)` - Check if user exists
- `User.register(username, repo)` - Register new user with validation

---

### Listing Model

**Data**: `listing_id`, `username`, `title`, `description`, `price`, `category`, `creation_time`

**Instance Methods**:
- `is_owned_by(username)` - Ownership check (case-insensitive)
- `delete(repo)` - Delete listing and update User/Category aggregates
- `get_sort_key_price()` / `get_sort_key_time()` - Sorting keys
- `format_time()` / `to_output_string()` - Output formatting

**Static Methods** (call repository):
- `Listing.create(username, title, description, price, category, repo)` - Create listing with validation, update aggregates
- `Listing.get_by_id(listing_id, repo)` - Retrieve listing

---

### Category Model

**Data**: `name`, `listing_ids` (set)

**Instance Methods**:
- `add_listing(listing_id)` / `remove_listing(listing_id)` - Manage category listings
- `get_listing_count()` / `has_listings()` - Query category state
- `get_listings(repo)` - Fetch all listings in this category

**Static Methods** (call repository):
- `Category.get_by_name(name, repo)` - Retrieve category
- `Category.get_top_category(repo)` - Find category with most listings

---

## Layer 3: Commands (Application Layer)

**Files**: `commands/user_commands.py`, `commands/listing_commands.py`, `commands/category_commands.py`

**Base**: `commands/base.py` - Abstract base class with `Repository` dependency.

**Purpose**: Handle user interaction and orchestrate model operations.

### UserCommand
```python
def register(self, *args) -> str:
    User.register(username, self.storage)  # Calls model
    return "Success"
```

### ListingCommand
```python
def create_listing(self, *args) -> str:
    listing = Listing.create(username, title, description,
                            price_str, category, self.storage)
    return str(listing.listing_id)

def get_listing(self, *args) -> str:
    if not User.exists(username, self.storage):
        return "Error - unknown user"
    listing = Listing.get_by_id(listing_id, self.storage)
    return listing.to_output_string()

def delete_listing(self, *args) -> str:
    listing = Listing.get_by_id(listing_id, self.storage)
    if not listing.is_owned_by(username):
        return "Error - listing owner mismatch"
    listing.delete(self.storage)
    return "Success"
```

### CategoryCommand
```python
def get_category(self, *args) -> str:
    category = Category.get_by_name(category_name, self.storage)
    listings = category.get_listings(self.storage)
    listings.sort(key=lambda x: x.get_sort_key_price())
    return "\n".join(listing.to_output_string() for listing in listings)

def get_top_category(self, *args) -> str:
    top_category = Category.get_top_category(self.storage)
    return top_category
```

---

## Data Flow Example: Creating a Listing

1. **User Input**: `CREATE_LISTING user1 'iPhone' 'New' 500 'Electronics'`

2. **Command Layer** (`commands/listing_commands.py`):
   - Calls `Listing.create(username, title, description, price, category, self.storage)`

3. **Model Layer** (`models/listing.py`):
   - Validates price
   - Checks user exists via `repo.get_user()`
   - Gets listing ID via `repo.get_next_listing_id()`
   - Creates Listing object
   - Saves listing via `repo.save_listing()`
   - Updates User aggregate: `user.add_listing()` + `repo.save_user()`
   - Updates Category aggregate: `category.add_listing()` + `repo.save_category()`

4. **Repository Layer** (`storage/repository.py`):
   - Performs pure dict read/write operations

5. **Response**: Command returns `"100001"` to user

---

## Key Design Principles

### 1. Commands Never Access Repository Directly

Commands only call model methods. The repository reference (`self.storage`) is passed to model methods, not used directly.

### 2. Models Contain All Business Logic

Validation, business rules, and aggregate management happen in models:
- Price validation in `Listing.create()`
- User existence check in `Listing.create()`
- Ownership validation in `listing.is_owned_by()`
- Aggregate updates (User, Category) in `Listing.create()` and `listing.delete()`

### 3. Repository is Pure Storage

No validation, no business rules - just save/get/delete operations.

---

## Design Patterns

- **Repository Pattern** - Data access abstraction, easy to swap storage backend
- **Domain-Driven Design** - Rich domain models with encapsulated business logic
- **Aggregate Pattern** - User and Category manage their own `listing_ids`
- **Factory Method** - Static `create()`/`register()` methods for entity creation
- **Command Pattern** - Each command is a separate method on a command handler

---

## Project Structure

```
├── main.py                      # Entry point, STDIN loop
├── commands/
│   ├── base.py                  # Abstract Command base class
│   ├── user_commands.py         # REGISTER
│   ├── listing_commands.py      # CREATE_LISTING, GET_LISTING, DELETE_LISTING
│   └── category_commands.py     # GET_CATEGORY, GET_TOP_CATEGORY
├── models/
│   ├── user.py                  # User aggregate
│   ├── listing.py               # Listing entity
│   └── category.py              # Category aggregate
├── storage/
│   └── repository.py            # Pure CRUD data storage
└── parsers/
    └── command_parser.py        # shlex-based command parsing
```
