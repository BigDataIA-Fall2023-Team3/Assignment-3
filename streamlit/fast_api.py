from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel
import openai
import pinecone
import requests
import openai

# Initialize your FastAPI app
app = FastAPI()

pinecone.init(api_key='8381828c-e892-4641-8aeb-d886c93e8df6', environment='gcp-starter')
index = pinecone.Index('bigdata')

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

@app.post("/search/")
async def search(query_model: Query, openai_model: OpenAIModel):
    
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
async def answer_question(query_model: QueryModel, openai_model: OpenAIModel):
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

