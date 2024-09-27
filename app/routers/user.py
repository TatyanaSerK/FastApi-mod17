from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session  # Сессия БД
from sqlalchemy import insert, select, update, delete  # Функции работы с записями.
from slugify import slugify  # Функция создания slug-строки
from typing import Annotated  # Аннотации, Модели БД и Pydantic.
from app.backend.db_depends import get_db  # Функция подключения к БД
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User).where(User.is_active == True)).all()
    return users

@router.get("/user_id/tasks")
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    tasks_user = db.scalars(select(Task).where(Task.user_id == user.id)).all()
    task_and_user = [user.id] + [i.id for i in tasks_user]
    task_by_user = db.scalars(
        select(Task).where(User.user_id.in_(task_and_user),
                              Task.is_active == True)).all()
    return task_by_user


    # subcategories = db.scalars(select(User).where(User.id == user.id)).all()
    # categories_and_subcategories = [user.id] + [i.id for i in subcategories]
    # products_category = db.scalars(
    #     select(Task).where(Task.user_id.in_(categories_and_subcategories),
    #                        Task.is_active == True,)).all()
    # return products_category



#
@router.get("/user_id")
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    return user


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int,
                      update_user_models: UpdateUser):
    user_update = db.scalar(select(User).where(User.id == user_id))
    if user_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    db.execute(update(User).where(User.id == user_id).values(
                                        firstname=update_user_models.firstname,
                                        lastname=update_user_models.lastname,
                                        age=update_user_models.age,
                                        slug=slugify(update_user_models.firstname)))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user_delete = db.scalar(select(User).where(User.id == user_id))
    db.delete(user_delete)
    user_task_delete = db.scalar(select(Task).where(Task.user_id == user_id))
    db.delete(user_task_delete)
    if user_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful'
    }
