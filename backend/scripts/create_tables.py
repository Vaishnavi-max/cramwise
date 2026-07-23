from app.db.database import Base, engine

# Import all models so SQLAlchemy knows about them
from app.db.models import Subject, Unit, Topic, TextBook, ReferenceBook


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")


if __name__ == "__main__":
    create_tables()