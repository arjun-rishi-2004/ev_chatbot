from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import spacy
from fuzzywuzzy import process

import json

class Query(BaseModel):
    question: str


app = FastAPI()
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

with open("faqs.json", "r", encoding="utf-8") as file:
    faq_data = json.load(file)

@app.get("/")
def read_root():
    return {"Hello": "World"}

def preprocess_text(text: str) -> str:
    doc = nlp(text.lower().strip())
    print(doc)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])  
def get_best_match(query: str) -> str:
    query = preprocess_text(query)
    print("query : ", query)
    best_match, score = process.extractOne(query, faq_data.keys())

    if score > 80: 
        return faq_data[best_match]
    else:
        return "Sorry, I don't have an answer for that. Please check the help section."


@app.post("/chatbot/")
async def chatbot_response(query: Query):
    question = query.question
    
    response = get_best_match(question)
    
    return {"response": response}

