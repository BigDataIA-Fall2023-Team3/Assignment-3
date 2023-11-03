import streamlit as st
import pandas as pd
import requests
import PyPDF2
import tiktoken
from textblob import TextBlob
import openai
import time
import os
import io
import pinecone
import boto3
import numpy as np



try:
    pinecone.init(api_key='', environment='gcp-starter')
    index = pinecone.Index('bigdata')
    print("Pinecone initialization and index creation successful.")
except Exception as e:
    print("An error occurred:", str(e))

s3_bucket = 'csv07'
s3_object_key = 'filenames.csv'



# Configure AWS credentials
os.environ['AWS_ACCESS_KEY_ID'] = 
os.environ['AWS_SECRET_ACCESS_KEY'] = 
# openai.api_key = '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'
s3_client = boto3.client('s3')

local_csv_file_path = "./extract.csv"
s3_client.download_file(s3_bucket, s3_object_key, local_csv_file_path)

openai.api_key = os.getenv('OPENAI_API')
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"




########################################################################################################################################

def options_list():
    # Read the file names from a CSV file
    filename_df = pd.read_csv('filenames.csv', header=None)  # No header specified
    # Extract the options as a list
    options = filename_df[0].tolist()[1:] 
    options =  [i.strip() for i in options]
    options.append('All')
    return options


def gen_embed(chunk_list):
    embed_list = []
    openai.api_key = 
    for i in chunk_list:
        text_embedding_response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=i,
        )
        text_embedding = text_embedding_response["data"][0]["embedding"]
        embed_list.append(text_embedding)
        time.sleep(20)
    return embed_list


def extract_sentences(text):
    blob = TextBlob(text)
    sentence_list = []
    # Iterate through the sentences and append them to the list
    for sentence in blob.sentences:
        sentence_list.append(sentence.raw)
    return sentence_list


def extract_text_with_pypdf2(pdf_content):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ""
    meta_data = pdf_reader.metadata
    meta_data = list(meta_data.values())[0]
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return [meta_data,text]


def create_chunk_list(sentence_list):
    l = len(sentence_list)
    chunk_list = []
    chunk = ''
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    for i in range(l):
        chunk+=sentence_list[i]
        if len(encoding.encode(chunk))<3000:
            if i==l-1:
                chunk_list.append(chunk)
            continue
        else:
            chunk_list.append(chunk)
            chunk = ''
    return chunk_list


def extract_pdf_content(link):
    filename = link.split('/')[-1]
    pdf_response = requests.get(link)
    pdf_content = pdf_response.content
    meta_data, pdf_text = extract_text_with_pypdf2(pdf_content)
    sentences_list = extract_sentences(pdf_text.strip())
    chunk_list = create_chunk_list(sentences_list)
    embeddings_list = gen_embed(chunk_list)
    df_temp = pd.DataFrame({'Filename':filename,'Metadata': meta_data,'Text': chunk_list, 'Embeddings':embeddings_list})
    
    # st.write(df_temp.head(10))
    return df_temp.copy()


############################################################################################################################################

def get_ids_from_query(index,input_vector):
  results = index.query(vector=input_vector, top_k=10000,include_values=False)
  ids = set()
  for result in results['matches']:
    ids.add(result['id'])
  return ids


def get_all_ids_from_index(index, num_dimensions, namespace=""):
  num_vectors = index.describe_index_stats()["namespaces"][namespace]['vector_count']
  all_ids = set()
  while len(all_ids) < num_vectors:
    input_vector = np.random.rand(num_dimensions).tolist()
    ids = get_ids_from_query(index,input_vector)
    all_ids.update(ids)
    return all_ids


def add_to_pinecone(df):
    starting_index = max([int(i) for i in get_all_ids_from_index(index,1536)])+1
    df['Index'] = range(starting_index, starting_index + len(df))
    df['Index'] = df['Index'].astype(str)

    # Setting batch size as 32
    batch_size = 32
    for i in range(0, len(df), batch_size):
        batch_df = df[i:i + batch_size]
        id_list = batch_df['Index'].tolist()
        embeds = batch_df['Embeddings'].tolist()
        text_list = batch_df['Text'].tolist()
        file_list = batch_df['Filename'].tolist()
        metalist = batch_df['Metadata'].tolist()
        m_list = []
        for i in range(len(text_list)):
            m = {'Filename': file_list[i], 'Text': text_list[i], 'Metadata': metalist[i]}
            m_list.append(m)
        to_upsert = zip(id_list, embeds, m_list) 
        index.upsert(vectors=list(to_upsert))

    


def upload_csv_to_s3(name):
    file_path = "filenames.csv"  # Replace with the path to your existing CSV file
    df = pd.read_csv(file_path)

    # Create a new DataFrame with the additional file name
    data_to_add = {'Name': [name]}
    df_to_add = pd.DataFrame(data_to_add)

    # Concatenate the two DataFrames
    combined_df = pd.concat([df, df_to_add], ignore_index=True)

    # Write the combined DataFrame back to the CSV file
    combined_df.to_csv(file_path, index=False)
     # Upload the CSV file, replacing it if it already exists.
    s3_client.upload_file("filenames.csv", 'csv07', "filenames.csv")

######################################################################################################################################

def search_pinecone_and_return_text(query):
    pinecone.init(api_key='', environment='gcp-starter')
    index = pinecone.Index('bigdata')
    openai.api_key = ""
    xq = openai.Embedding.create(input=query, engine="text-embedding-ada-002")['data'][0]['embedding']
    # st.write(xq)
    res = index.query(xq, top_k=2, include_metadata=True)
    st.write(res)
    results = []
    for match in res['matches']:
        metadata = match.get('metadata', {})  # Use .get() to handle missing 'metadata'
        text = metadata.get('text', '')  # Use .get() to handle missing 'text'
        results.append(text)
    
    return results


def filtered_search(query,filename):
    openai.api_key = "
    xq = openai.Embedding.create(input=query, engine="text-embedding-ada-002")['data'][0]['embedding']
    res = index.query(
    vector=xq,
    filter={
        "Filename": {"$eq": filename}
    },
    top_k=2,
    include_metadata=True
    )
    results = []
    print()
    for match in res['matches']:
        metadata = match.get('metadata', {})  # Use .get() to handle missing 'metadata'
        text = metadata.get('text', '')  # Use .get() to handle missing 'text'
        results.append(text)
    return results

def construct_prompt(context,query):
    prompt = """Answer the question as truthfully as possible using the context below, and if the answer is no within the context, say 'I don't know.'"""
    prompt += "\n\n"
    prompt += "Context: " + context
    prompt += "\n\n"
    prompt += "Question: " + query
    prompt += "\n"
    prompt += "Answer: "
    return prompt


def answer_question(results, query):
    st.write(results)
    # Build the prompt with the search results and the user's question
    prompt = construct_prompt(results,query)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response
    


    



##############################################################################################################################

st.title("QA Chatbot")
# Create a textbox for user input
link = st.text_input("Enter pdf link")
# Create an update button
update_button = st.button("Update database")


# Check if the update button is clicked
if update_button:
    if not link:
        st.warning("Please enter pdf link")
    else:
        filename = link.split('/')[-1]
        df = extract_pdf_content(link)
        add_to_pinecone(df)
        upload_csv_to_s3(filename)
        st.success("Updated")

#############################################################################################################################

options = options_list()
selected_option = st.selectbox("Select a file name:", options)

# Create another textbox for user input
question = st.text_input("Enter question")

# Create a submit button
submit_button = st.button("Submit")

# Check if the submit button is clicked
if submit_button:
    if not question:
        st.warning("Please enter question")
    else:
        if selected_option=='All':
            st.write(question)
            res = search_pinecone_and_return_text(question)
            context = res[0]
            # a = answer_question(context,question)
            st.write(context)
        else:
            res = filtered_search(question,selected_option)
            context = res[0]
            # a =answer_question(context,question)
            st.write(context)
            
        
