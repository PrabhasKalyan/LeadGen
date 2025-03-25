import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


def rag(query):
    loader = TextLoader('./output.txt')
    documents = loader.load()

    embeddings = GPT4AllEmbeddings()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Set chunk size
        chunk_overlap=50  # Optional overlap for better context continuity
    )
    split_docs = text_splitter.split_documents(documents)

    embeddings = GPT4AllEmbeddings()

    vectorstore = Chroma.from_documents(
        split_docs,
        embeddings
    )
    

    relevant_docs = vectorstore.similarity_search(query, k=3)


    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"""
        Context information:
        {context}
        
        Question: {query}
        
        Based on the context above, please provide a detailed and precise answer to the question.
        """    
    print(prompt)






