from storage.repository import Repository


class Command:
    """Base class for all command handlers."""

    def __init__(self, storage: Repository):
        self.storage = storage
