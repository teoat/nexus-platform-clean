from database.connection import get_database_connection


def get_db():
    """Dependency to get a database connection"""
    with get_database_connection() as db:
        yield db


class DatabaseManager:
    """Database manager for handling database operations"""

    def __init__(self):
        pass

    async def initialize(self):
        """Initialize database connection"""
        # Placeholder - database initialization would go here
        pass

    def get_db(self):
        """Get database session"""
        return get_db()


# Create instance
database_manager = DatabaseManager()
