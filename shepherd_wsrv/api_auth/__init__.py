import asyncio

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from shepherd_wsrv.api_user.models import User
from shepherd_wsrv.api_user.utils_misc import verify_password_hash

from .models import AccessToken
from .utils import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> AccessToken:
    await asyncio.sleep(1)  # rate limit
    _user = await User.by_email(form_data.username)
    if not _user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password_hash(form_data.password, _user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if _user.email_confirmed_at is None:
        raise HTTPException(status_code=400, detail="Email is not yet verified")
    return create_access_token(_user.email)
