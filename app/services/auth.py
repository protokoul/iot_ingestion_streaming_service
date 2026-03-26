from fastapi import HTTPException, status

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.accounts import AccountRepository


class AuthService:
    def __init__(self, repo: AccountRepository, settings: Settings) -> None:
        self.repo = repo
        self.settings = settings

    async def signup(self, username: str, password: str) -> dict[str, str]:
        try:
            await self.repo.create(username=username, hashed_password=hash_password(password))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        token = create_access_token(subject=username, settings=self.settings)
        return {"access_token": token, "token_type": "bearer"}

    async def login(self, username: str, password: str) -> dict[str, str]:
        account = await self.repo.get_by_username(username)
        if not account or not verify_password(password, account["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        token = create_access_token(subject=username, settings=self.settings)
        return {"access_token": token, "token_type": "bearer"}

    async def bootstrap_admin(self) -> None:
        existing = await self.repo.get_by_username(self.settings.bootstrap_admin_username)
        if existing:
            return
        await self.repo.create(
            username=self.settings.bootstrap_admin_username,
            hashed_password=hash_password(self.settings.bootstrap_admin_password),
        )
