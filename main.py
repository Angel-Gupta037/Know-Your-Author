from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import sqlite3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

def init_db():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            status TEXT DEFAULT 'want to read',
            rating INTEGER,
            notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reading_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            book_title TEXT,
            order_num INTEGER,
            why_start_here TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/home")
def home_page():
    return FileResponse("static/index.html")
    
@app.get("/my-list")
def my_list_page():
    return FileResponse("static/my-list.html")

@app.get("/about")
def about_page():
    return FileResponse("static/about.html")

@app.get("/")
def home():
    return {"message": "Welcome to Know Your Author"}

@app.get("/author/{author_name}")
def get_author_by_name(author_name: str):
    url = f"https://openlibrary.org/search/authors.json?q={author_name}"
    response = requests.get(url)
    data = response.json()
    
    if data["numFound"] == 0:
        return {"error": "Author not found"}
    
    first_result = data["docs"][0]
    return {
        "name": first_result.get("name"),
        "birth_date": first_result.get("birth_date"),
        "work_count": first_result.get("work_count")
    }
@app.get("/author/{author_name}/books")
def get_author_books(author_name: str):
    url = f"https://openlibrary.org/search.json?author={author_name}&limit=20"
    response = requests.get(url)
    data = response.json()
    
    if data["numFound"] == 0:
        return {"error": "No books found"}
    
    books = []
    for book in data["docs"]:
        books.append({
            "title": book.get("title"),
            "year": book.get("first_publish_year"),
        })
    
    return {"author": author_name, "books": books}

class Book(BaseModel):
    title: str
    author: str

@app.post("/books")
def add_book(book: Book):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    
    # check if this author already exists in reading list
    cursor.execute("SELECT id FROM books WHERE author=?", (book.author,))
    existing = cursor.fetchone()
    
    cursor.execute(
        "INSERT INTO books (title, author) VALUES (?, ?)",
        (book.title, book.author)
    )
    conn.commit()
    conn.close()
    
    if not existing:
        message = f"✨ You have entered {book.author}'s world! Welcome to the journey."
    else:
        message = f"📚 '{book.title}' added! Going deeper into {book.author}'s universe."
    
    return {"message": message}

@app.get("/books")
def get_books():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return {"books": books}
class ReadingPath(BaseModel):
    author: str
    book_title: str
    order_num: int
    why_start_here: str

@app.post("/reading-path")
def add_reading_path(path: ReadingPath):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reading_paths (author, book_title, order_num, why_start_here) VALUES (?, ?, ?, ?)",
        (path.author, path.book_title, path.order_num, path.why_start_here)
    )
    conn.commit()
    conn.close()
    return {"message": f"📖 Added '{path.book_title}' to {path.author}'s reading path!"}

@app.get("/author/{author_name}/where-to-start")
def where_to_start(author_name: str):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT book_title, order_num, why_start_here FROM reading_paths WHERE author=? ORDER BY order_num",
        (author_name,)
    )
    path = cursor.fetchall()
    conn.close()
    
    if not path:
        return {"message": f"No reading path found for {author_name} yet. Check back soon!"}
    
    return {
        "author": author_name,
        "reading_path": [
            {"order": p[1], "book": p[0], "why": p[2]} for p in path
        ]
    }
@app.put("/books/{book_id}")
def update_book(book_id: int, status: str, rating: int = None, notes: str = None):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    cursor.execute(
        "UPDATE books SET status=?, rating=?, notes=? WHERE id=?",
        (status, rating, notes, book_id)
    )
    conn.commit()
    conn.close()

    title = book[0] if book else "This book"

    if status == "reading":
        message = f"📖 '{title}' and you are now on an adventure together!"
    elif status == "finished":
        message = f"🎉 '{title}' has been conquered! How did it feel?"
    else:
        message = f"🔖 '{title}' is patiently waiting for you..."

    return {"message": message}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

    title = book[0] if book else "That book"
    return {"message": f"💔 '{title}' has left your world... goodbye old friend."}