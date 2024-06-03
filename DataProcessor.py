import streamlit as st
from langchain_community.document_loaders import PyPDFLoader 
import os
import tempfile
import uuid
from langchain_google_vertexai import VertexAIEmbeddings
import sys
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma

sys.path.append(os.path.abspath('../../'))
class DocumentProcessor:
    def __init__(self):
        self.pages = []  # List to keep track of pages from all documents
    
    def ingest_documents(self):
        # Render a file uploader widget. Replace 'None' with the Streamlit file uploader code.
        uploaded_files = st.file_uploader(label="Upload your pdfs",type='pdf',accept_multiple_files=True)
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                # Generate a unique identifier to append to the file's original name
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(uploaded_file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
                # Write the uploaded PDF to a temporary file
                with open(temp_file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                # Use PyPDFLoader here to load the PDF and extract pages.
                current_pdf = PyPDFLoader(temp_file_path)
                self.pages.extend(current_pdf.load_and_split())
                # Clean up by deleting the temporary file.
                os.unlink(temp_file_path)      
            # Display the total number of pages processed.
            st.write(f"Total pages processed: {len(self.pages)}")
        if len(self.pages)>=1:
            return True
        else:
            return False
        
class EmbeddingClient:
    def __init__(self, model_name, project, location):
        # Initialize the VertexAIEmbeddings client with the given parameters
        self.client = VertexAIEmbeddings(model_name=model_name,project=project,location=location)
        
    def embed_query(self, query):
        vectors = self.client.embed_query(query)
        return vectors
    
    def embed_documents(self, documents):
        try:
            return self.client.embed_documents(documents)
        except AttributeError:
            print("Method embed_documents not defined for the client.")
            return None
        
        
class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        
        self.processor = processor    
        self.embed_model = embed_model  
        self.db = None            
    
    def create_chroma_collection(self):
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return
        text_splitter= CharacterTextSplitter(separator="\n",chunk_size=200,chunk_overlap=30)
        texts= text_splitter.split_documents(self.processor.pages)
        if texts is not None:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")

        self.db = Chroma.from_documents(texts,self.embed_model)
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")
        return self.db
    def query_chroma_collection(self, query) -> Document:
    
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

