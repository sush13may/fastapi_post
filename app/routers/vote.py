
from fastapi import FastAPI, APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import Session

from app import oauth2
from .. import models, schemas, database, oauth2

router = APIRouter(
    prefix = "/votes",
    tags = ['Votes']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote:schemas.Vote, db:Session=Depends(database.get_db),
current_user:int=Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id== vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id: {vote.post_id} does not exist")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)

    found_vote = vote_query.first()

    if vote.dir == 1 :
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has alredy voted on post {vote.post_id}")

        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added Vote to the Post"}
    else:

        if not found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has alredy voted on post {vote.post_id}")

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "Successfuly Deleted Vote from the Post"}


