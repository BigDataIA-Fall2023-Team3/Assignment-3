from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import database as db
import psycopg2
from jwt import PyJWTError



class Token(BaseModel):
    access_token: str
    token_type: str

from jwt_auth import create_access_token
from jwt_auth import decode_access_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(security=oauth2_scheme)

# This utility will provide a way for our routes to get the current user.
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str

class UserInDB(User):
    email: str
    hashed_password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    new_password: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Mock database functions
def get_user(username: str):
    conn = db.get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT username, email, password FROM users WHERE username=%s;", (username,))
            user_data = cur.fetchone()
            if user_data:
                user_dict = {
                    "username": user_data[0],
                    "email": user_data[1],
                    "hashed_password": user_data[2]
                }
                return UserInDB(**user_dict)
        except psycopg2.Error as e:
            print("Error fetching user.")
            print(e)
        finally:
            cur.close()
            conn.close()
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Here, we decode the token. In a real-world scenario, you'd also verify its validity, expiration, etc.
    try:
        payload = decode_access_token(token)
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# You'd replace the next line with your actual database call
@app.post("/register")
async def register_user(username: str, email: str, password: str):
    if db.user_exists(username):
        return {"error": "Username already exists"}
    db.add_user(username, email, password)
    return {"status": "User registered successfully"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    stored_password = db.get_password_hash(form_data.password)  # Get hashed password from database
    print(f"Stored Password: {stored_password}")
    
    if db.check_user(form_data.username, form_data.password):
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@app.get("/users", response_model=UserInDB)  # Modified this line
async def read_users_details(current_user: UserInDB = Depends(get_current_user)):  # Renamed for clarity
    return current_user


@app.put("/users/update", response_model=User)
async def update_user_info(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    # You can update user information here based on the data in user_update
    if user_update.email is not None:
        # Update the user's email
        db.update_user_email(current_user.username, user_update.email)

    if user_update.new_password is not None:
        # Update the user's password
        db.update_user_password(current_user.username, user_update.new_password)

    # Fetch the updated user information
    updated_user = get_user(current_user.username)
    return updated_user
