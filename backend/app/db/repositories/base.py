from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.db.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model_class: type[T]):
        self._db = db
        self._model = model_class

    def all(self) -> list[T]:
        return self._db.query(self._model).all()

    def get(self, id: str) -> T | None:
        return self._db.get(self._model, id)

    def add(self, instance: T) -> T:
        self._db.add(instance)
        self._db.commit()
        self._db.refresh(instance)
        return instance

    def add_all(self, instances: list[T]) -> list[T]:
        self._db.add_all(instances)
        self._db.commit()
        return instances

    def delete_all(self) -> None:
        self._db.query(self._model).delete()
        self._db.commit()

    def replace_all(self, instances: list[T]) -> list[T]:
        self.delete_all()
        return self.add_all(instances)
