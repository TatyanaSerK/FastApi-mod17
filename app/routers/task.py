from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session  # Сессия БД
from sqlalchemy import insert, select, update, delete  # Функции работы с записями.
from slugify import slugify  # Функция создания slug-строки
from typing import Annotated  # Аннотации, Модели БД и Pydantic.
from app.backend.db_depends import get_db  # Функция подключения к БД
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateTask, UpdateTask

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task).where(Task.is_active == True)).all()
    return tasks


@router.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(User).where(Task.id == task_id))
    if task is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    return task


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], create_task_mod: CreateTask):
    db.execute(insert(User).values(id=create_task_mod.id,
                                   title=create_task_mod.title,
                                   content=create_task_mod.content,
                                   priority=create_task_mod.priority,
                                   user_id=create_task_mod.user_id,
                                   slug=slugify(create_task_mod.name),
                                   user=create_task_mod.user))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int,
                      update_task_model: UpdateTask):
    task_update = db.scalar(select(Task).where(Task.id == task_id))
    if task_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Task was not found')
    db.execute(update(Task).where(Task.id == task_id).values(
        title=update_task_model.title,
        content=update_task_model.content,
        priority=update_task_model.priority,
        user_id=update_task_model.user_id,
        slug=slugify(update_task_model.name),
        user=update_task_model.user))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }



@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task_delete = db.scalar(select(Task).where(Task.id == task_id))
    if task_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(update(Task).where(Task.id == task_id).values(is_active=False))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful'
    }
