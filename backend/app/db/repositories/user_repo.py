from sqlalchemy.orm import Session

from app.db.models import OrganizationModel, UserModel
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, db: Session):
        super().__init__(db, UserModel)

    def by_email(self, email: str) -> UserModel | None:
        return self._db.query(UserModel).filter(UserModel.email == email).first()


class OrganizationRepository(BaseRepository[OrganizationModel]):
    def __init__(self, db: Session):
        super().__init__(db, OrganizationModel)

    def by_name(self, name: str) -> OrganizationModel | None:
        return self._db.query(OrganizationModel).filter(OrganizationModel.name == name).first()
