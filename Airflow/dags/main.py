# import os
# from airflow.models import DAG
# from airflow.operators.bash_operator import BashOperator
# from airflow.operators.python_operator import PythonOperator
# from airflow.utils.dates import days_ago
# from airflow.models.param import Param
# from datetime import timedelta
# from airflow.models import BaseOperator
# from airflow.utils.decorators import apply_defaults

# import PyPDF2
# import requests


# dag = DAG(
#     dag_id="sandbox",
#     schedule="0 0 * * *",   # https://crontab.guru/
#     start_date=days_ago(0),
#     catchup=False,
#     dagrun_timeout=timedelta(minutes=60),
#     tags=["labs", "damg7245"],
#     # params=user_input,
# )

# class PDFProcessingOperator(BaseOperator):
    
#     def __init(
#         self,
#         pdf_url,
#         output_csv_file,
#         *args, **kwargs
#     ):
#         super(PDFProcessingOperator, self).__init__(*args, **kwargs)
#         self.pdf_url = pdf_url
#         self.output_csv_file = output_csv_file

#     def execute(self, context):
#         # Fetch the PDF content from the URL
#         pdf_response = requests.get(self.pdf_url)
#         pdf_content = pdf_response.content

#         # Extract text from the PDF
#         pdf_text = self.extract_text_with_pypdf2(pdf_content)

#         # Implement data validation checks here if needed

#         # Generate embeddings and metadata for chunked texts if required

#         # Save the extracted data to a CSV file
#         self.save_to_csv(pdf_text)

#     def extract_text_with_pypdf2(self, pdf_content):
#         pdf_reader = PyPDF2.PdfFileReader(pdf_content)
#         text = ""
#         for page_num in range(pdf_reader.numPages):
#             page = pdf_reader.getPage(page_num)
#             text += page.extractText()
#         return text

#     def save_to_csv(self, pdf_text):
#         with open(self.output_csv_file, "w") as csv_file:
#             csv_file.write(pdf_text)



# def print_keys(**kwargs):
#     print("-----------------------------")
#     print(f"Your Secret key is: {os.getenv('OPENAI_KEY')}") # Donot print this anywhere, this is just for demo
#     print("-----------------------------")

# with dag:
#     hello_world = BashOperator(
#         task_id="hello_world",
#         bash_command='echo "Hello from airflow"'
#     )

#     fetch_keys = PythonOperator(
#         task_id='fetch_keys',
#         python_callable=print_keys,
#         provide_context=True,
#         dag=dag,
#     )
    
#     # # Example usage in an Airflow DAG
#     pdf_processing_task = PDFProcessingOperator(
#         task_id="process_pdf",
#         pdf_url="https://www.sec.gov/files/form1-a.pdf",  # Replace with your PDF URL
#         output_csv_file="//Users/keerthi/Desktop/Assignment-3/Airflow/dags/output.csv",  # Specify the output CSV file path
#         dag=dag,
#     )


#     bye_world = BashOperator(
#         task_id="bye_world",
#         bash_command='echo "Bye from airflow"'
#     )

#     hello_world>> fetch_keys>> pdf_processing_task >> bye_world import os
import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import PyPDF2
import requests

# Function to extract content from a PDF link
def extract_pdf_content(pdf_url, output_csv_file):
    pdf_response = requests.get(pdf_url)
    pdf_content = pdf_response.content
    pdf_text = extract_text_with_pypdf2(pdf_content)
    save_to_csv(pdf_text, output_csv_file)

def extract_text_with_pypdf2(pdf_content):
    pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(pdf_content))
    text = ""
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text += page.extractText()
    return text

def save_to_csv(pdf_text, output_csv_file):
    with open(output_csv_file, "w") as csv_file:
        csv_file.write(pdf_text)

def print_keys(**kwargs):
    print("-----------------------------")
    print(f"Your Secret key is: {os.getenv('OPENAI_KEY')}") # Don't print this anywhere; this is just for demo
    print("-----------------------------")

# Define your Airflow DAG
dag = DAG(
    dag_id="sandbox",
    schedule_interval="0 0 * * *",   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["labs", "damg7245"],
    # params=user_input,
)

# Tasks
hello_world = BashOperator(
    task_id="hello_world",
    bash_command='echo "Hello from airflow"',
    dag=dag,
)

fetch_keys = PythonOperator(
    task_id='fetch_keys',
    python_callable=print_keys,
    provide_context=True,
    dag=dag,
)

pdf_processing_task = PythonOperator(
    task_id="process_pdf",
    python_callable=extract_pdf_content,
    op_args=["https://www.sec.gov/files/form1-a.pdf", "/Users/keerthi/Desktop/Assignment-3/Airflow"],
    dag=dag,
)

bye_world = BashOperator(
    task_id="bye_world",
    bash_command='echo "Bye from airflow"',
    dag=dag,
)

# Define task dependencies
hello_world >> fetch_keys >> pdf_processing_task >> bye_world






# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from datetime import datetime
# import PyPDF2
# import requests





# # Function to extract content from a PDF link
# def extract_pdf_content(pdf_url, output_file):
#     response = requests.get(pdf_url)
#     with open(output_file, 'wb') as pdf_file:
#         pdf_file.write(response.content)

#     with open(output_file, 'rb') as pdf_file:
#         pdf_reader = PyPDF2.PdfFileReader(pdf_file)
#         text_content = ""
#         for page_num in range(pdf_reader.numPages):
#             page = pdf_reader.getPage(page_num)
#             text_content += page.extractText()
#     return text_content

# # Define your Airflow DAG
# with DAG('pdf_extraction_dag', start_date=datetime(2023, 10, 29)) as dag:
#     pdf_url = "https://www.sec.gov/files/form1-a.pdf"  # Replace with your PDF URL
#     output_file = "/Users/keerthi/Desktop/Assignment-3/Airflow/dags/output.pdf"  # Define the path where you want to save the downloaded PDF
#     output_text_file = "/Users/keerthi/Desktop/Assignment-3/Airflow/dags/output.txt"  # Define the path where you want to save the extracted text

#     def extract_pdf_content_task():
#         text_content = extract_pdf_content(pdf_url, output_file)
#         with open(output_text_file, 'w', encoding='utf-8') as text_file:
#             text_file.write(text_content)

#     pdf_extraction_task = PythonOperator(
#         task_id='extract_pdf_content',
#         python_callable=extract_pdf_content_task,
#     )

#     # Define task dependencies
#     pdf_extraction_task

# You can further customize task dependencies as needed


# You can define task dependencies as needed
