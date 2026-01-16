from fastapi import FastAPI

app = FastAPI()

@app.get("/home")
def get_users():
    return{
        "message": "This is license Management System"
    }



