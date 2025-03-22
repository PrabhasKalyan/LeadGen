import gspread
from google.oauth2.service_account import Credentials
SERVICE_ACCOUNT_FILE = "trusty-bearing-443508-h4-7baec02fe256.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", 
          "https://www.googleapis.com/auth/drive"]


creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)


NEW_SHEET_NAME = "My New Workbook"
spreadsheet = client.create(NEW_SHEET_NAME)

YOUR_EMAIL = "prabhakalyan0473@gmail.com"
spreadsheet.share(YOUR_EMAIL, perm_type="user", role="writer")


print(f"New Google Sheet created: {spreadsheet.url}")




import json
from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
import langgraph.graph
from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import langgraph

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url = "https://api.groq.com/openai/v1",
    temperature=0
)

search = TavilySearchResults(max_results=2)
app=FastAPI()



def search(prompt,state):
    prompt = prompt  + "\nAnalyze the following query and determine whether it requires a web search to answer accurately. Return only 'Yes' if a web search or real-time data is needed, otherwise return 'No'. Do not provide any explanation or additional text."  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def websearch(prompt):

    prompt = prompt 
    search_results = search.invoke(prompt)
    response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role": "user", "content":f"Analyse this {search_results}and answer the question :{prompt} in one word "}
    ])
    print(response.choices[0].message.content)
    return response.choices[0].message.content



def llm_search(prompt):
    prompt = prompt  + "\n Do not provide any explanation or additional text just give me the answer"  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    print(response.choices[0].message.content)
    return response.choices[0].message.content



workflow = langgraph.graph()
workflow.add_node("search_test",search)
workflow.add_node("websearch",websearch)
workflow.add_node("llm_search",llm_search)

workflow.add_conditional_edges("search_test",
                               lambda state:state,{
                                   "Yes":"websearch",
                                   "No":"llm_search"
                               })


workflow.set_entry_point("search_test")
app=workflow.compile()


