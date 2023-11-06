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


pinecone.init(api_key='8381828c-e892-4641-8aeb-d886c93e8df6', environment='gcp-starter')
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
    prompt = """Answer the question as truthfully as possible using the context below, and if the answer is no within the context, say 'I don't know.'"""
    prompt += "\n\n"
    prompt += "Context: " + context
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
    print(f"Stored Password: {stored_password}")
    
    if db.check_user(form_data.username, form_data.password):
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise credentials_exception

async def get_protected_resource(current_user: UserInDB = Depends(get_current_user)):
    return {"message": "This is a protected resource"}


@app.get("/users", response_model=UserInDB)  # Modified this line
async def read_users_details(current_user: UserInDB = Depends(get_current_user)):  # Renamed for clarity
    return current_user


@app.post("/search/")
async def search(query_model: Query, openai_model: OpenAIModel, current_user: UserInDB = Security(get_current_user)):
    
    openai.api_key = openai_model.api_key
    
    # Get the query embedding
    xq = openai.Embedding.create(input=query_model.query, engine="text-embedding-ada-002")['data'][0]['embedding']
    # st.write(xq)
    res = index.query(xq, top_k=2, include_metadata=True)
    results = []
    for match in res['matches']:
        metadata = match.get('metadata', {})  # Use .get() to handle missing 'metadata'
        text = metadata.get('text', '')  # Use .get() to handle missing 'text'
        results.append(text)
    
    return results

@app.post("/answer/")
async def answer_question(query_model: QueryModel, openai_model: OpenAIModel, current_user: UserInDB = Security(get_current_user)):
    openai.api_key =openai_model.api_key
    # Perform a filtered search if a filename is provided
    if query_model.filename and query_model.filename.lower() != 'all':
        # Create an embedding of the query
        xq = openai.Embedding.create(input=query_model.query, engine="text-embedding-ada-002")['data'][0]['embedding']
        # Filter the search by the given filename
        res = index.query(
            vector=xq,
            filter={"Filename": {"$eq": query_model.filename}},
            top_k=2,
            include_metadata=True
        )
    else:
        # If 'All' or no filename is provided, perform a regular search
        xq = openai.Embedding.create(input=query_model.query, engine="text-embedding-ada-002")['data'][0]['embedding']
        res = index.query(xq, top_k=2, include_metadata=True)

    # Extract the text from search results
    results = [match.get('metadata', {}).get('text', '') for match in res['matches']]
    
    # Use the first search result as context for generating the answer
    context = results[0] if results else ""

    # Build the prompt with the search results and the user's question
    prompt = construct_prompt(context, query_model.query)
    
    # Generate the answer with OpenAI API using the prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response

