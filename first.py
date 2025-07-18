from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {'message':'Hello world'}

@app.get("/about")
def about():
    return {'message':'CAmpusx is a educational plateform where you can learn ai'}