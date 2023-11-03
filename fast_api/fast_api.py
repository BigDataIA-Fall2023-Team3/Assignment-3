from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import database as db
import psycopg2
import jwt
import logging  
import boto3
import uuid
import os

# Initialize the logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set the desired log level (e.g., INFO, DEBUG)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)



class Token(BaseModel):
    access_token: str
    token_type: str


from jwt_auth import create_access_token
from jwt_auth import decode_access_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(security=oauth2_scheme)


class User(BaseModel):
    username: str

class UserInDB(User):
    email: str
    hashed_password: Optional[str] = None
    logs: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    new_password: Optional[str] = None


def upload_log_to_s3(username, log_message):
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = 'us-east-1'
# boto3.setup_default_session(region_name=aws_region)
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,region_name=aws_region)

    bucket_name = 'big-data-assignment-3'

    # Generate a unique object key for each log entry using UUID
    object_key = f'logs/{username}/{uuid.uuid4()}.log'

    try:
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=log_message)
        return f's3://{bucket_name}/{object_key}'  # Return the S3 object path
    except Exception as e:
        logger.error(f"Failed to upload log to S3 for user '{username}': {str(e)}")
        return None  # Return None to indicate failure



def get_user(username: str):
    conn = db.get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT username, email, logs FROM users WHERE username=%s;", (username,))
            user_data = cur.fetchone()
            if user_data:
                user_dict = {
                    "username": user_data[0],
                    "email": user_data[1],
                    "logs": user_data[2]
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
    except Exception:
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




@app.post("/register")
async def register_user(username: str, email: str, password: str):
    if db.user_exists(username):
        logger.error(f"Registration failed for user '{username}': Username already exists")
        return {"error": "Username already exists"}
    
    registration_log_message = f"User '{username}' registered successfully."
    
    s3_object_path = upload_log_to_s3(username, registration_log_message)
    if s3_object_path:
        # If upload is successful, store the S3 object path in the database
        db.add_user(username, email, password, s3_object_path)
        return {"status": "User registered successfully"}
    else:
        return {"error": "Failed to upload registration log to S3"}



@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    stored_password = db.get_password_hash(form_data.password)  # Get hashed password from database
    print(f"Stored Password: {stored_password}")
    
    if db.check_user(form_data.username, form_data.password):
        access_token = create_access_token(data={"sub": form_data.username})
        logger.info(f"User '{form_data.username}' logged in successfully.")
        return {"access_token": access_token, "token_type": "bearer"}
    
    logger.error(f"Login failed for user '{form_data.username}': Incorrect username or password")
    raise credentials_exception




async def get_protected_resource(current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"User '{current_user.username}' accessed protected resource.")
    return {"message": "This is a protected resource"}




@app.get("/users", response_model=UserInDB)  # Modified this line
async def read_users_details(current_user: UserInDB = Depends(get_current_user)):  # Renamed for clarity
    logger.info(f"User '{current_user.username}' requested their details.")
    return current_user




@app.put("/users/update", response_model=User)
async def update_user_info(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    # You can update user information here based on the data in user_update
    if user_update.email is not None:
        # Update the user's email
        db.update_user_email(current_user.username, user_update.email)
        logger.info(f"User '{current_user.username}' updated their email.")
    
    if user_update.new_password is not None:
        # Update the user's password
        db.update_user_password(current_user.username, user_update.new_password)
        logger.info(f"User '{current_user.username}' updated their password.")
    
    # Fetch the updated user information
    updated_user = get_user(current_user.username)
    return updated_user