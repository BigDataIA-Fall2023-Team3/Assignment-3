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

# Function to extract content from a PDF link
def extract_pdf_content(pdf_url, output_csv_file):

    pdf_response = requests.get(pdf_url)
    pdf_content = pdf_response.content
    pdf_text = extract_text_with_pypdf2(pdf_content)
    save_to_csv(pdf_text, output_csv_file)
    upload_csv_to_s3(output_csv_file, 'extract.csv')



def extract_text_with_pypdf2(pdf_content):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ""
   
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def save_to_csv(pdf_text, output_csv_file):
    print("the path is "+output_csv_file)
    with open(output_csv_file, "w") as csv_file:
        print("Testing if in")
        csv_file.write(pdf_text)

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
    s3_client.upload_file(csv_file_path, 'csv007', s3_object_key)


dag = DAG(
    dag_id="sandbox",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["labs", "damg7245"],
    # params=user_input,
)


pdf_processing_task = PythonOperator(
    task_id="process_pdf",
    python_callable=extract_pdf_content,
    op_args=["https://www.sec.gov/files/form1-a.pdf", "output.csv"],
    dag=dag,
)




# Define task dependencies
pdf_processing_task

