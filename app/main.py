from fastapi import FastAPI
from sqlalchemy import engine
from .database import engine
from .config import settings
from . import models
from app.routers import post, user, vote, auth
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Hello World pushing out to ubuntu"}
#if __name__ == '__main__':
    
 #   uvicorn.run(app, port=8080, host='127.0.0.1')



