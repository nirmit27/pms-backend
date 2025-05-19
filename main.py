"""Root of the application."""

from fastapi import FastAPI

app = FastAPI()

# Route handlers


@app.get("/")
def index():
    return {"message": "Hello friend."}


@app.get("/about")
def about():
    return {"message": "I am your friend."}
