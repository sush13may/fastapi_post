from os import stat
from fastapi import FastAPI, status, HTTPException,Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from starlette.responses import Response
from sqlalchemy import func
from app import oauth2
from ..database import get_db
from .. import models
from .. import schemas

router = APIRouter(
    prefix = "/posts",
    tags = ["Posts"]
)


@router.get("/",response_model=List[schemas.PostOut])
def get_post(db: Session=Depends(get_db),current_user:int= Depends(oauth2.get_current_user),
limit:int=10, skip:int=0, search:Optional[str]=""):
    print(limit)
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
   
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote,
     models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    print(posts)
    return posts


@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post:schemas.PostCreate,db: Session=Depends(get_db),
current_user:int= Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=current_user.id,**post.dict())
    #new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/{id}", response_model=schemas.PostOut)
def single_post(id: int,db: Session=Depends(get_db)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'post with {id} does not exist!')
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db:Session=Depends(get_db),current_user:int= Depends(oauth2.get_current_user)):
    query= db.query(models.Post).filter(models.Post.id == id)

    query_result = query.first()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail=f'post with {id} does not exist!')
    
    if query_result.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'post with {id} does not exist in current user')

    query.delete(synchronize_session=False)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.Post )
def update_post(id:int,to_update:schemas.PostCreate, db:Session=Depends(get_db),current_user:int= Depends(oauth2.get_current_user)):
    query= db.query(models.Post).filter(models.Post.id == id)

    query_result = query.first()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'post with {id} does not exist!')
    
    if query_result.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'post with {id} does not exist in current user')

    
    query.update(to_update.dict(), synchronize_session=False)

    db.commit()
    return query_result


