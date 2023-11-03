from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import database as db
import psycopg2
import openai
import pinecone
import requests
import re
import os


pinecone.init(api_key=os.environ['PINECONE_API_KEY'], environment='gcp-starter')
index = pinecone.Index('bigdata')

class Token(BaseModel):
    access_token: str
    token_type: str


from jwt_auth import create_access_token
from jwt_auth import decode_access_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(security=oauth2_scheme)


class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(BaseModel):
    username: str
    email: str
    logs: Optional[str] = None

class QueryModel(BaseModel):
    query: str
    filename: str = None

class Query(BaseModel):
    query: str

class OpenAIModel(BaseModel):
    api_key: str

def construct_prompt(context,query):
    prompt = """Use the below content only to answer the question. If no content is found say No answer\n\n"""
    prompt += "Content: " + context
    prompt += "\n\n"
    prompt += "Question: " + query
    prompt += "\n"
    prompt += "Answer: "
   
    return prompt

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

def is_valid_email(email):
    # Define a regular expression pattern for a valid email format
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    # Use the re.match() function to check if the email matches the pattern
    return re.match(email_pattern, email) is not None


@app.post("/register")
async def register_user(user: User):
    if db.user_exists(user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    if db.email_exists(user.email):
        raise HTTPException(status_code=401, detail="Email already exists")
    if not is_valid_email(user.email):
        raise HTTPException(status_code=402, detail="Invalid email format")
    logs = ""
    db.add_user(user.username, user.email, user.password, logs)
    return {"message": "User created successfully"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    stored_password = db.get_password_hash(form_data.password)  # Get hashed password from database
    
    
    if db.check_user(form_data.username, form_data.password):
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=None)
        return {"access_token": access_token, "token_type": "bearer"}
    raise credentials_exception

async def get_protected_resource(current_user: UserInDB = Depends(get_current_user)):
    return {"message": "This is a protected resource"}


@app.get("/users", response_model=UserInDB)  # Modified this line
async def read_users_details(current_user: UserInDB = Depends(get_current_user)):  # Renamed for clarity
    return current_user



@app.post("/answer/")
async def answer_question(query_model: QueryModel, openai_model: OpenAIModel, current_user: UserInDB = Security(get_current_user)):
    openai.api_key =openai_model.api_key
    if query_model.filename.lower() == 'all':
        # Create an embedding of the query
        xq = openai.Embedding.create(input=query_model.query, engine="text-embedding-ada-002")['data'][0]['embedding']
        res = index.query(
            vector=xq,
            top_k=1,
            include_metadata=True
        )
    else:
        
        xq = openai.Embedding.create(input=query_model.query, engine="text-embedding-ada-002")['data'][0]['embedding']
        res = index.query(
            vector=xq,
            top_k=1,
            include_metadata=True,
            filter={"Filename": {"$eq": query_model.filename}}
        )

    # Extract the text from search results
    if len(res['matches']) == 0:
        results = ''
    else:
        results = res['matches'][0]['metadata']['Text']

    # Build the prompt with the search results and the user's question
    prompt = construct_prompt(results, query_model.query)
    
    
    # Generate the answer with OpenAI API using the prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response

