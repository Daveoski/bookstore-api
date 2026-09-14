from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


# ============================================================
# USER MODEL
# ============================================================

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    username: str = Field(
        max_length=100,
        unique=True,
        index=True,
    )

    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
    )

    hashed_password: str = Field(
        max_length=255,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


# ============================================================
# AUTHOR MODEL
# ============================================================

class Author(SQLModel, table=True):
    __tablename__ = "authors"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    name: str = Field(
        max_length=200,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
        unique=True,
    )

    bio: str | None = Field(
        default=None,
    )

    books: list["Book"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        },
    )


# ============================================================
# BOOK MODEL
# ============================================================

class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    title: str = Field(
        max_length=255,
    )

    description: str | None = Field(
        default=None,
    )

    price: int

    author_id: int = Field(
        foreign_key="authors.id",
        index=True,
    )

    author: Author | None = Relationship(
        back_populates="books",
    )