import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings

os.environ["OPENAI_API_KEY"]="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"


def rag(query):
    loader = TextLoader('./output.txt')
    documents = loader.load()

    embeddings = GPT4AllEmbeddings()

    vectorstore = Chroma.from_documents(
            documents,
            embeddings
            )

    query="What does this company do?"

    relevant_docs = vectorstore.similarity_search(query, k=3)
    # llm = GPT4All(model="gpt-4o-mini")

    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"""
        Context information:
        {context}
        
        Question: {query}
        
        Based on the context above, please provide a detailed and precise answer to the question.
        """    
    print(prompt)



rag("What does this company do?")


