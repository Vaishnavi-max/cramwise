from app.db.database import SessionLocal
from app.db.models import (
    Subject,
    Unit,
    Topic,
    TextBook,
    ReferenceBook,
)


class DatabaseLoader:
    def __init__(self):
        self.session = SessionLocal()

    def close(self):
        self.session.close()

    def save_subject(self, parsed_data):
        subject = Subject(
            course_name=parsed_data["course_name"],
            course_code=parsed_data["course_code"],
            semester=parsed_data["semester"],
            credits=parsed_data["credits"],
        )

        self.session.add(subject)
        self.session.flush()

        return subject

    def save_units(self, subject, units):
        for unit_data in units:

            unit = Unit(
                subject=subject,
                unit_name=unit_data["unit_name"],
            )

            self.session.add(unit)
            self.session.flush()

            self.save_topics(
                unit,
                unit_data.get("topics", [])
            )

    def save_topics(self, unit, topics):
        for topic_name in topics:

            topic = Topic(
                unit=unit,
                topic_name=topic_name,
                parent_topic_id=None
            )

            self.session.add(topic)

    def save_books(self, subject, text_books, reference_books):

        for book in text_books:

            textbook = TextBook(
                subject=subject,
                book_name=book
            )

            self.session.add(textbook)

        for book in reference_books:

            referencebook = ReferenceBook(
                subject=subject,
                book_name=book
            )

            self.session.add(referencebook)

    def save(self, parsed_data):
        try:
            subject = self.save_subject(parsed_data)

            self.save_units(
                subject,
                parsed_data["units"]
            )

            self.save_books(
                subject,
                parsed_data["text_books"],
                parsed_data["reference_books"]
            )

            self.session.commit()

        except Exception:
            self.session.rollback()
            raise

        finally:
            self.close()