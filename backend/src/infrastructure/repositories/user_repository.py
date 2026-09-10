from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user import User, Role
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.database.models import UserModel

class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session


    def _to_entity(self, model: UserModel) -> User:
        return User(
            user_id=model.user_id,
            email=model.email,
            password_hash=model.password_hash,
            username=model.username,
            fullname=model.fullname,
            role=Role(model.role.value),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            user_id=user.user_id,
            email=user.email,
            password_hash=user.password_hash,
            username=user.username,
            fullname=user.fullname,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)


    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.user_id == user_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Return a paginated list of all users."""
        result = await self._session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, user: User) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.user_id == user.user_id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User {user.user_id} not found")

        model.email = user.email
        model.password_hash = user.password_hash
        model.role = user.role
        model.is_active = user.is_active
        model.updated_at = user.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
    
    async def delete(self, user_id: int) -> bool:
        """Delete the store row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if model: 
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False