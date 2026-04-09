from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "BACKEND KE FRONT END NYA DAH CONNECT YGY"}