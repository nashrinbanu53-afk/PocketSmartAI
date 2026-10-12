from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from ..schemas import RegisterRequest, LoginRequest
from ..database import create_user, get_user_by_email
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Authentication"])

def _set_cookie(response, token):
    response.set_cookie(
        "access_token", token, httponly=True, samesite="lax",
        max_age=86400, secure=False
    )

@router.post("/register")
def register(data: RegisterRequest):
    if get_user_by_email(data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user_id = create_user(data.name.strip(), data.email, hash_password(data.password))
    return {"message": "Registration successful", "user_id": user_id}

@router.post("/login")
def login(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["id"])
    response = JSONResponse({
        "message": "Login successful",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    })
    _set_cookie(response, token)
    return response

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.post("/token")
def token(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user["id"]), "token_type": "bearer"}
