from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

def create_embedding(texts):
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    return embeddings

def create_vectorstore(texts, embeddings):
    db = Chroma.from_texts(texts, embeddings)
    return db

def create_retriever(db):
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 1})
    return retriever

def retrieve_documents(retriever, sub_queries):
    retrieved_docs = []
    for sub_query in sub_queries:
        sub_query = sub_query.strip()
        if sub_query:
            # print(f"Retrieving for sub-query: '{sub_query}'")
            results = retriever.get_relevant_documents(sub_query)
            for result in results:
                if isinstance(result.page_content, str):
                    retrieved_docs.append(result.page_content)
                else:
                    print(f"Non-string result found: {result.page_content}")
    return retrieved_docs
