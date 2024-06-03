from fastapi import APIRouter, HTTPException, status, Depends
from schemas import SignUpModel, SignUpModelResponse, LoginModel
from models import User
from database import get_db
from sqlalchemy.orm import Session
from utility import pwd_context, verify_password, get_user
from schemas import Token
from auth import create_access_token, create_refresh_token, get_current_user
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from datetime import timedelta


auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


ACCESS_TOKEN_EXPIRE_DAYS = 1
REFRESH_TOKEN_EXPIRE_DAYS = 2


@auth_router.get('/')
def home(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user is None:
        return {"Message": "Unauthorized"}
    user_data = db.query(User).filter(User.id == current_user.id).first()
    return {"Message": f"Hello {user_data.username}, your email is {user_data.email}"}

@auth_router.post('/signup', response_model=SignUpModelResponse,
                  status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel, db: Session = Depends(get_db)):
    db_email = db.query(User).filter(User.email == user.email).first()
    print(">>>>>>>>", db_email)
    if db_email is not None:
        print("db_email is none")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the email already exists"
        )

    db_username = db.query(User).filter(User.username == user.username).\
        first()
    if db_username is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail="User with the username already exists")

    hashed_password = pwd_context.hash(user.password)

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    db.add(new_user)
    db.commit()
    # db.refresh(new_user)
    print(f"New user created: {new_user}")

    response = SignUpModelResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        password=new_user.password,
        is_active=new_user.is_active,
        is_staff=new_user.is_staff


    )
    return response


@auth_router.post('/login')
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
                ):
    db_user = db.query(User).filter(User.username == user.username).\
        first()
    
    if db_user and verify_password(user.password, db_user.password):
        access_token = create_access_token(data={"username": user.username})

        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
       
        refresh_token = create_refresh_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_token_expires.total_seconds(),
            "refresh_token": refresh_token
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

 
# Refresh tokens

from fastapi import HTTPException, status

@auth_router.get('/refresh')
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        refresh_token = create_refresh_token(data={"sub": current_user.username})
        return {"refresh_token": refresh_token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating refresh token: {str(e)}"
        )