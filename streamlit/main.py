import streamlit as st

import requests


st.title("Welcome to SEC Data Vector Search Platform!")
st.write("""
    Dive deep into a sophisticated search experience optimized for the vast world of SEC documents. Built with a vision to harness the potential of machine learning and provide users with the most relevant results, this platform offers the following:

    - **Automated Processing**: Our advanced Airflow pipelines ensure seamless data acquisition, embedding generation, and populating the Pinecone vector database. With automated embedding from a rich sample set of PDF files, our system continually evolves and improves.

    - **Customized Search**: Choose from a variety of preprocessed forms, ranging from documents to templates. Our state-of-the-art similarity search mechanism queries the Pinecone vector database to fetch you the best results. Whether you filter by a specific form or decide to go broad, our search has got you covered.

    - **User-Centric Design**: Create your account securely, log in, and enjoy a personalized Question Answering interface. Your security is our utmost priority, and we ensure it with cutting-edge JWT authentication for all our API endpoints.

    - **Transparency & Accountability**: Every operation is logged for auditing and troubleshooting, ensuring you always have clarity and control.

    Our platform is a blend of robust backend engineering, streamlined front-end experience, and top-tier cloud deployment. Whether you're a researcher, student, or just curious, our platform is designed to cater to your SEC document needs. So, sign up, log in, and start exploring!
    """)




# Define a list of PDF links
pdf_links_list = [
    "https://www.sec.gov/files/form1-z.pdf",
    "https://www.sec.gov/files/form1.pdf",
    "https://www.sec.gov/files/form1-a.pdf",
    "https://www.sec.gov/files/form1-e.pdf",
    "https://www.sec.gov/files/form10.pdf"
]

# Create a Streamlit dropdown to select a PDF link
selected_pdf_link = st.selectbox("Select a PDF link", pdf_links_list)

# Create a text input for asking questions
question = st.text_input("Ask a question")

# Create a button to trigger the chatbot
if st.button("Ask Chatbot"):
    # Construct the request payload
    payload = {
        "conf": {
            "pdf_links_list": [selected_pdf_link],
            "question": question
        }
    }

    # Set the Airflow DAG URL
    # airflow_url = "https://airflow-server-url/airflow/api/v1/dags/csv_generation/dagRuns"
    airflow_url="http://localhost:8080/dags/pdf_processing_dag/dagRuns"
    

    # Send a POST request to trigger the pipeline
    response = requests.post(airflow_url, json=payload)

    # Display the response from the pipeline
    st.write(response.text)