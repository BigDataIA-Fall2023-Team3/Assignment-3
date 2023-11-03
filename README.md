## Assignment-3

# Automating Metadata Extraction and Document Retrieval System

#### [streamlit app](https://assignment-3.streamlit.app/)

#### [Heroku](https://assignment-3-b24bd7fda897.herokuapp.com/docs)

#### [codelabs](https://codelabs-preview.appspot.com/?file_id=16mdL8dZQ83-4-dlF7DsDiW4hhAcy46rbm-nsTOuCowg)

## Open AI Interactive Chat Bot

### Project Description:

This project, "Automating Metadata Extraction and Document Retrieval System," is a culmination of two distinct pipelines and a client-facing application that integrates Airflow, FastAPI, Streamlit, and Pinecone. The goal of this assignment is to automate the extraction of metadata and document embeddings from a sample set of PDF files and create a user-friendly interface for querying and retrieving information efficiently.



### Technology Stack:
- Airflow
- Docker
- GCP
- AWS
- PostgreSQL Database
- Streamlit
- PyPdf
- FastAPI
- Heroku
- Open AI
- Jupyter
- Pinecone Vector Database

### Architecture

![part - 1](https://github.com/BigDataIA-Fall2023-Team3/Assignment-3/assets/114708712/3e6327d3-1fd1-42da-ae35-508f40ac2cca)
![part-2](https://github.com/BigDataIA-Fall2023-Team3/Assignment-3/assets/114708712/fa2a77dd-43d1-4057-9d2a-9fa8869b9630)

### Navigation


### Youtube


### Flow of the Project:

1. Airflow is utilized to create 2 Pipelines
- One for Data Acquisition and Embeddings generation
- Another for Insertion of Embeddings and chunks in Pinevector Database
2. Utilizing Open AI A chat bot is modelled to query the data in database
3. User registration and authentication is done through fast api
4. The User Interface is provided through streamlit


WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT

AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK

 ### Contributions: 

- Sumanayana Konda: 31.3%
- Akshatha Patil: 33.3%
- Ruthwik Bommenahalli Gowda: 33.3%
- Pavan Madhav Manikantha Sai Nainala: 2%
