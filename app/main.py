from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
)
from app.database import get_session
from app.models import Author, Book, User
from app.schemas import (
    AuthorCreate,
    AuthorResponse,
    AuthorUpdate,
    BookCreate,
    BookResponse,
    BookUpdate,
    Token,
    UserCreate,
    UserResponse,
)


app = FastAPI(
    title="Bookstore API",
    description=(
        "A complete Bookstore REST API built with "
        "FastAPI, SQLModel, PostgreSQL, Alembic and JWT."
    ),
    version="1.0.0",
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to the Bookstore API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):

    username_statement = select(User).where(
        User.username == user_data.username
    )

    existing_username = session.exec(
        username_statement
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    email_statement = select(User).where(
        User.email == user_data.email
    )

    existing_email = session.exec(
        email_statement
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        ),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@app.post(
    "/login",
    response_model=Token,
    tags=["Authentication"],
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):

    user = authenticate_user(
        session,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    token = create_access_token(
        user.username
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get(
    "/me",
    response_model=UserResponse,
    tags=["Authentication"],
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return current_user


# ============================================================
# AUTHOR CRUD
# ============================================================

@app.post(
    "/authors",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authors"],
)
def create_author(
    author_data: AuthorCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if author_data.email:

        statement = select(Author).where(
            Author.email == author_data.email
        )

        existing_author = session.exec(
            statement
        ).first()

        if existing_author:
            raise HTTPException(
                status_code=400,
                detail="Author email already exists",
            )

    author = Author(
        name=author_data.name,
        email=author_data.email,
        bio=author_data.bio,
    )

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


@app.get(
    "/authors",
    response_model=list[AuthorResponse],
    tags=["Authors"],
)
def get_authors(
    session: Session = Depends(get_session),
):

    statement = select(Author)

    return session.exec(statement).all()


@app.get(
    "/authors/{author_id}",
    response_model=AuthorResponse,
    tags=["Authors"],
)
def get_author(
    author_id: int,
    session: Session = Depends(get_session),
):

    statement = select(Author).where(
        Author.id == author_id
    )

    author = session.exec(statement).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found",
        )

    return author


@app.put(
    "/authors/{author_id}",
    response_model=AuthorResponse,
    tags=["Authors"],
)
def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    statement = select(Author).where(
        Author.id == author_id
    )

    author = session.exec(statement).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found",
        )

    update_data = author_data.model_dump(
        exclude_unset=True
    )

    if (
        "email" in update_data
        and update_data["email"]
    ):

        duplicate_statement = select(Author).where(
            Author.email == update_data["email"],
            Author.id != author_id,
        )

        duplicate = session.exec(
            duplicate_statement
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Author email already exists",
            )

    for key, value in update_data.items():
        setattr(author, key, value)

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


@app.delete(
    "/authors/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Authors"],
)
def delete_author(
    author_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    statement = select(Author).where(
        Author.id == author_id
    )

    author = session.exec(statement).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found",
        )

    session.delete(author)
    session.commit()

    return None


# ============================================================
# BOOK CRUD
# ============================================================

@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
)
def create_book(
    book_data: BookCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    author_statement = select(Author).where(
        Author.id == book_data.author_id
    )

    author = session.exec(
        author_statement
    ).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found",
        )

    book = Book(
        title=book_data.title,
        description=book_data.description,
        price=book_data.price,
        author_id=book_data.author_id,
    )

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


@app.get(
    "/books",
    response_model=list[BookResponse],
    tags=["Books"],
)
def get_books(
    session: Session = Depends(get_session),
):

    statement = select(Book)

    return session.exec(statement).all()


@app.get(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
)
def get_book(
    book_id: int,
    session: Session = Depends(get_session),
):

    statement = select(Book).where(
        Book.id == book_id
    )

    book = session.exec(statement).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return book


@app.put(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    statement = select(Book).where(
        Book.id == book_id
    )

    book = session.exec(statement).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    update_data = book_data.model_dump(
        exclude_unset=True
    )

    if "author_id" in update_data:

        author_statement = select(Author).where(
            Author.id == update_data["author_id"]
        )

        author = session.exec(
            author_statement
        ).first()

        if not author:
            raise HTTPException(
                status_code=404,
                detail="Author not found",
            )

    for key, value in update_data.items():
        setattr(book, key, value)

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Books"],
)
def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    statement = select(Book).where(
        Book.id == book_id
    )

    book = session.exec(statement).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    session.delete(book)
    session.commit()

    return None