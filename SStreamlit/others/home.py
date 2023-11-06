import streamlit as st

def app():
    st.title('Welcome to the Chatbot App')
    st.write("This is the home page.")
    st.write("Please sign up or sign in to continue to the chatbot.")

    st.write("""
        Dive deep into a sophisticated search experience optimized for the vast world of SEC documents. Built with a vision to harness the potential of machine learning and provide users with the most relevant results, this platform offers the following:

        - **Automated Processing**: Our advanced Airflow pipelines ensure seamless data acquisition, embedding generation, and populating the Pinecone vector database. With automated embedding from a rich sample set of PDF files, our system continually evolves and improves.

        - **Customized Search**: Choose from a variety of preprocessed forms, ranging from documents to templates. Our state-of-the-art similarity search mechanism queries the Pinecone vector database to fetch you the best results. Whether you filter by a specific form or decide to go broad, our search has got you covered.

        - **User-Centric Design**: Create your account securely, log in, and enjoy a personalized Question Answering interface. Your security is our utmost priority, and we ensure it with cutting-edge JWT authentication for all our API endpoints.

        - **Transparency & Accountability**: Every operation is logged for auditing and troubleshooting, ensuring you always have clarity and control.

        Our platform is a blend of robust backend engineering, streamlined front-end experience, and top-tier cloud deployment. Whether you're a researcher, student, or just curious, our platform is designed to cater to your SEC document needs. So, sign up, log in, and start exploring!
        """)
    
