from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Book Library API")

# Templates
templates = Jinja2Templates(directory="templates")

# In-memory storage
books = {}
book_id_counter = 1

# MODELS
class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    rating: float = Field(ge=0, le=5)
    description: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    rating: Optional[float] = Field(None, ge=0, le=5)
    description: Optional[str] = None

class BookOut(BaseModel):
    id: int
    title: str
    rating: float
    description: Optional[str] = None
    archived: bool = False

# DEPENDENCY
def verify_token(token: str = Query(None)):
    if not token or token != "secret123":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token

# PART 1
@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}

# PART 2
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/square", summary="Calculate square", description="Returns the square of a number")
def square(number: int):
    return {"number": number, "square": number ** 2}

# PART 3
@app.post("/books", response_model=BookOut, status_code=201)
def create_book(book: BookCreate):
    global book_id_counter
    new_book = BookOut(
        id=book_id_counter,
        title=book.title,
        rating=book.rating,
        description=book.description,
        archived=False
    )
    books[book_id_counter] = new_book
    book_id_counter += 1
    return new_book

@app.put("/books/{id}", response_model=BookOut)
def update_book(id: int, book: BookUpdate):
    if id not in books:
        raise HTTPException(status_code=404, detail="Not Found")
    
    existing = books[id]
    updated_data = book.dict(exclude_unset=True)
    updated_book = existing.copy(update=updated_data)
    books[id] = updated_book
    return updated_book

# PART 5
@app.get("/books")
def get_books():
    active_books = [b for b in books.values() if not b.archived]
    if not active_books:
        raise HTTPException(status_code=204)
    return active_books

@app.get("/books/{id}")
def get_book(id: int):
    if id < 0:
        raise HTTPException(status_code=400, detail="Invalid ID")
    if id not in books:
        raise HTTPException(status_code=404, detail="Not Found")
    book = books[id]
    if book.archived:
        raise HTTPException(status_code=410, detail="Gone")
    return book

@app.delete("/books/{id}", status_code=204)
def delete_book(id: int):
    if id < 0:
        raise HTTPException(status_code=400, detail="Invalid ID")
    if id not in books:
        raise HTTPException(status_code=404, detail="Not Found")
    book = books[id]
    if book.archived:
        raise HTTPException(status_code=410, detail="Gone")
    book.archived = True
    books[id] = book
    return None

# PART 6
@app.get("/books/html", response_class=HTMLResponse)
def books_list_html(request: Request):
    active_books = [b for b in books.values() if not b.archived]
    return templates.TemplateResponse("list.html", {
        "request": request,
        "books": active_books
    })

@app.get("/books/{id}/html", response_class=HTMLResponse)
def book_detail_html(request: Request, id: int):
    if id not in books:
        raise HTTPException(status_code=404, detail="Not Found")
    book = books[id]
    if book.archived:
        raise HTTPException(status_code=410, detail="Gone")
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "book": book
    })

# PART 7: Secure Route
@app.get("/secure-data", dependencies=[Depends(verify_token)])
def secure_data():
    return {"message": "Secure data access granted"}

#uvicorn main:app --reload