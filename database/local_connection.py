"""
NEXUS Platform - Local Database Connection
SQLite database connection for local development
"""


# Local SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./nexus.db"


def create_local_engine():
    """Create SQLite engine for local development"""
    return create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )


# Create engine
engine = create_local_engine()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base
Base = declarative_base()
