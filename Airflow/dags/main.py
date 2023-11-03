import os
import io
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import PyPDF2
import requests
import csv
import boto3
import pandas as pd
from textblob import TextBlob
import nltk
nltk.download('punkt')
import openai
import tiktoken
import time


s3_bucket = 'csv07'
s3_object_key = 'extract.csv'
openai.api_key = os.getenv('OPENAI_API')
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
pdf_links_list = ["https://www.sec.gov/files/form1-z.pdf",
                  "https://www.sec.gov/files/form1.pdf",
                  "https://www.sec.gov/files/form1-a.pdf",
                  "https://www.sec.gov/files/form1-e.pdf",
                  "https://www.sec.gov/files/form10.pdf"
                  ]

# Function to extract content from a PDF link
def extract_pdf_content(links, output_csv_file):
    column_names = ["Meta Data", "Text", "Embeddings"]
    df = pd.DataFrame(columns=column_names)
    for i in links:
        pdf_response = requests.get(i)
        pdf_content = pdf_response.content
        meta_data, pdf_text = extract_text_with_pypdf2(pdf_content)
        sentences_list = extract_sentences(pdf_text.strip())
        # print(sentences_list[0])
        chunk_list = create_chunk_list(sentences_list)
        embeddings_list = gen_embed(chunk_list)
        df_temp = pd.DataFrame({'Meta Data': meta_data,'Text': chunk_list, 'Embeddings': embeddings_list})
        df = pd.concat([df, df_temp], ignore_index=True)
    df.to_csv(output_csv_file, index=True)
    upload_csv_to_s3(output_csv_file, 'extract.csv')


def extract_sentences(text):
    blob = TextBlob(text)
    sentence_list = []
    # Iterate through the sentences and append them to the list
    for sentence in blob.sentences:
        sentence_list.append(sentence.raw)
    return sentence_list


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



def gen_embed(chunk_list):
    embed_list = []
    for i in chunk_list:
        text_embedding_response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=i,
        )
        text_embedding = text_embedding_response["data"][0]["embedding"]
        embed_list.append(text_embedding)
        time.sleep(20)
    return embed_list



def extract_text_with_pypdf2(pdf_content):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ""
    # Access the metadata
    meta_data = pdf_reader.metadata
    meta_data = list(meta_data.values())[0]
    # Print metadata information
    # for key, value in meta_data.items():
    #     print(f"{key}: {value}")
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return [meta_data,text]



def print_csv(output_csv_file):
    with open(output_csv_file, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            print(row)



def upload_csv_to_s3(csv_file_path, s3_object_key):
    a_key = os.getenv('A_KEY')
    sa_key = os.getenv('SA_KEY')

    # Configure AWS credentials
    os.environ['AWS_ACCESS_KEY_ID'] = a_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = sa_key

    s3_client = boto3.client('s3')

    # Upload the CSV file, replacing it if it already exists.
    s3_client.upload_file(csv_file_path, 'csv07', s3_object_key)


def download_csv(file):
    a_key = os.getenv('A_KEY')
    sa_key = os.getenv('SA_KEY')

    # Configure AWS credentials
    os.environ['AWS_ACCESS_KEY_ID'] = a_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = sa_key

    s3_client = boto3.client('s3')

    # Download the CSV file from S3 to a local temporary file
    local_csv_file_path = "./extract.csv"
    s3_client.download_file(s3_bucket, s3_object_key, local_csv_file_path)

    # Print the CSV content
    with open(local_csv_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            print(row)
    



dag = DAG(
    dag_id="csv_generation",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["csv_file"],
    # params=user_input,
)



pdf_processing_task = PythonOperator(
    task_id="pdf_extract",
    python_callable=extract_pdf_content,
    op_args=[pdf_links_list, "output.csv"],
    dag=dag,
)


pdf_processing_task


dag2 = DAG(
    dag_id="download",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["database"],
    # params=user_input,
)


download_file = PythonOperator(
    task_id="csv_download",
    python_callable=download_csv,
    op_args=["output.csv"],
    dag=dag2,
)

download_file


