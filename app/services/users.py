from fastapi import HTTPException, status

from app.repositories.users import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def create(self, payload: dict) -> dict:
        try:
            return await self.repo.create(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    async def update(self, user_id: str, payload: dict) -> dict:
        updated = await self.repo.update(user_id, payload)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated

    async def get(self, user_id: str) -> dict:
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
