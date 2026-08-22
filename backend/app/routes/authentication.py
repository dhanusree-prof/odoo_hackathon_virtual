from fastapi import APIRouter
from app.utils.dependencies import DbSession
from app.schemas.user import LoginRequest, UserCreate, UserResponse
from app.services import authentication

router = APIRouter()


@router.post("/register")
def register(data: UserCreate, db: DbSession):
    return authentication.register(data, db)


@router.post("/login")
def login(data: LoginRequest, db: DbSession):
    return authentication.login(data, db)
