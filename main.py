from fastapi import FastAPI
import requests

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