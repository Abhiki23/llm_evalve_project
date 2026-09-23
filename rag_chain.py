## responsible for: retrieved context from vectorDB + User question -> LLM -> Answer

import os
from dotenv import load_dotenv
from groq import Groq
from retriever import retriever

## load env variables
load_dotenv()

## initialize groq client

client = Groq(api_key= os.getenv("GROQ_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")

## Main RAG Pipeline

def generate_answer(query: str):
    ## Step 1: retrieval
    context = retriever(query)

    ## Step 2: build prompt for LLM
    prompt = f"""
Context : {context}
Question: {query}
"""
    
    ## Step 3: Generation
    response = client.chat.completions.create(
        model = MODEL_NAME,
        messages = [
            {
                "role": "system",
                "content" : """
You are an enterprise Q&A Chatbot assistant. Answer the questions strictly ONLY on the information provided in the context.
if the answer is not present in the context, say "I DONT KNOW" . DO NOT INVENT THE answer or hallucinate information.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content