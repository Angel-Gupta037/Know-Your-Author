from fastapi import FastAPI
import requests
import sqlite3
from pydantic import BaseModel

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
    conn.commit()
    conn.close()

init_db()

app = FastAPI()

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
    url = f"https://openlibrary.org/search.json?author={author_name}&limit=5"
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
@app.put("/books/{book_id}")
def update_book(book_id: int, status: str, rating: int = None, notes: str = None):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
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

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    title = book[0] if book else "That book"
    return {"message": f"💔 '{title}' has left your world... goodbye old friend."}