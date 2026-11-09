from app.database import get_engine
from app.models import Base


def initialize_database() -> None:
    Base.metadata.create_all(bind=get_engine())


if __name__ == "__main__":
    initialize_database()
