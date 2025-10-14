from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(
    prefix="/api/books",
    tags=["books"],
    responses={404: {"description": "Not found"}}
)

# Storage
books_db = {}
counter = 1

# Models
class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    rating: float = Field(ge=0, le=5)
    description: Optional[str] = None

class BookOut(BaseModel):
    id: int
    title: str
    rating: float
    description: Optional[str] = None

@router.post("", response_model=BookOut, status_code=201)
def create_book(book: BookCreate):
    global counter
    new_book = BookOut(
        id=counter,
        title=book.title,
        rating=book.rating,
        description=book.description
    )
    books_db[counter] = new_book
    counter += 1
    return new_book

@router.get("")
def list_books():
    return list(books_db.values())

@router.get("/{id}")
def get_book(id: int):
    if id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[id]