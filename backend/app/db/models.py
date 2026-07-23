from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, nullable=False)
    course_name = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    credits = Column(Integer, nullable=False)

    units = relationship("Unit", back_populates="subject")
    textbooks = relationship("TextBook", back_populates="subject")
    reference_books = relationship("ReferenceBook", back_populates="subject")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String, nullable=False)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    subject = relationship("Subject", back_populates="units")
    topics = relationship("Topic", back_populates="unit")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, nullable=False)

    unit_id = Column(
        Integer,
        ForeignKey("units.id"),
        nullable=False
    )

    parent_topic_id = Column(
        Integer,
        ForeignKey("topics.id"),
        nullable=True
    )

    unit = relationship("Unit", back_populates="topics")

    parent_topic = relationship(
        "Topic",
        remote_side=[id]
    )


class TextBook(Base):
    __tablename__ = "textbooks"

    id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String, nullable=False)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    subject = relationship("Subject", back_populates="textbooks")


class ReferenceBook(Base):
    __tablename__ = "reference_books"

    id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String, nullable=False)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    subject = relationship("Subject", back_populates="reference_books")