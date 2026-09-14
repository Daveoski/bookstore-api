from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# AUTHOR SCHEMAS
# ============================================================

class AuthorCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )

    email: EmailStr | None = None

    bio: str | None = None


class AuthorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    email: EmailStr | None = None

    bio: str | None = None


class AuthorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr | None
    bio: str | None


# ============================================================
# BOOK SCHEMAS
# ============================================================

class BookCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    price: int = Field(
        ge=0,
    )

    author_id: int


class BookUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    price: int | None = Field(
        default=None,
        ge=0,
    )

    author_id: int | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    description: str | None
    price: int
    author_id: int