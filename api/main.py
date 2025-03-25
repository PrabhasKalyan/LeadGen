import json
from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
import langgraph.graph
from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import langgraph as lg
from langgraph.graph import Graph,END
from langchain.schema import HumanMessage,AIMessage
from rag import rag
from leadgen_agent import get_info
from scrape import scrape_website1,clean_body_content

os.environ["TAVILY_API_KEY"] = "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"

client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)

search = TavilySearchResults(max_results=2)
app=FastAPI()



def search1(state):
    prompt= state["messages"][-1].content
    prompt = prompt  + "\nAnalyze the following query and determine whether it requires a web search to answer accurately. Return only 'Yes' if a web search or real-time data is needed, otherwise return 'No'. Do not provide any explanation or additional text."  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    state = {"messages": state["messages"], "decision": response.choices[0].message.content}
    return state


def websearch(state):
    prompt= state["messages"][-1].content
    search_results = search.invoke(prompt)
    response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role": "user", "content":f"Analyse this {search_results}and answer the question :{prompt} Do not provide any explanation or additional text just give me the answer this is very importnt as it will go directly to google sheets "}
    ])
    state={"messages": state["messages"] + [AIMessage(response.choices[0].message.content)]}
    print(state["messages"][-1].content)
    return state


def llm_search(state):
    prompt= state["messages"][-1].content
    prompt = prompt  + "\n Do not provide any explanation or additional text just give me the answer"  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    print(response.choices[0].message.content)
    state={"messages": state["messages"] + [AIMessage(response.choices[0].message.content)]}
    return state



workflow = Graph()
workflow.add_node("search_test",search1)
workflow.add_node("websearch",websearch)
workflow.add_node("llm_search",llm_search)

workflow.add_conditional_edges("search_test",
                               lambda state:state["decision"],{
                                   "Yes":"websearch",
                                   "No":"llm_search"
                               })


workflow.set_entry_point("search_test")
workflow.add_edge("websearch", END)
workflow.add_edge("llm_search", END)
workflow_app=workflow.compile()


@app.post("/websearch")
def start(prompt):
    state = {"messages": [HumanMessage(content=prompt)]}
    output = workflow_app.invoke(state)
    print(output["messages"][-1].content)
    return output["messages"][-1].content


def invoke_llm(prompt):
    prompt = prompt  + "\nAnalyze the following query and describe it in 3-4 in breif and give only the answer and nothing else only the answer no explanations strictly"  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    info =response.choices[0].message.content
    return info

@app.post("/scrape_agent")
def search_agent(link,prompt):
    get_info(link,prompt)
    invoke_llm(rag(prompt))
    with open("output.txt", "w") as file:  # Open in write mode to overwrite contents
            pass



@app.post("/business_linkedin")
def business_linkedin(link):
     prompt ="""You are an AI expert in structuring business data. Given the raw text scraped from HTML of a LinkedIn company page, extract and return the following details in a structured json format:


1. **Company Name**: Extract the official name of the company.
2. **LinkedIn URL**: The URL of the company's LinkedIn page.
3. **Website URL**: The official website of the company.
4. **Industry**: The industry the company operates in.
5. **Company Size**: The number of employees (range, e.g., "51-200").
6. **Headquarters**: The location of the company’s headquarters.
7. **Year Founded**: The year the company was established.
8. **Company Type**: Whether it is a private, public, non-profit, etc.
9. **Company Description**: A short summary of what the company does.
10. **Specialties**: Key areas the company specializes in.
11. **Employee Count on LinkedIn**: The number of employees listed on LinkedIn not follower like(eg.View all 173 employees)).

                return only if the answer is known else return None
**Format the output as json**:"""
     with open("../output.txt", "w") as file:
        file.write("")
     scrape_website1(link)
     with open("../output.txt", "r") as file:
        text=file.read()
     info=invoke_llm(text + prompt)
    #  with open("../output.txt", "w") as file:
    #     pass
     return info

@app.post("/personal_linkedin")
def personal_linkedin(link):
     prompt ="""You are an AI expert in structuring business data. Given the raw text scraped from the HTML of a LinkedIn personal profile page, extract and return the following details in a structured JSON format:  

                1. **Full Name**: The person's full name.  
                2. **Current Job Title**: Their current role/position.  
                3. **Current Company**: The company they are currently working at.  
                4. **Location**: Their current location (city, country).  
                5. **Industry**: The industry they work in.  
                6. **Education**: Their educational background.  
                7. **Connections Count**: Number of LinkedIn connections (e.g., 500+).  
                8. **Profile Summary**: A brief description of their professional background.  
                9. **Skills**: A list of key skills mentioned in their profile.  
                10. **Work Experience**: A structured list of past job roles, including company names, positions, and durations.  

                **Return `None` for any missing or unavailable data.**  

                **Format the output as JSON.**  
                """
     with open("../output.txt", "w") as file:
        file.write("")
     scrape_website1(link)
     with open("../output.txt", "r") as file:
        text=file.read()
     info=invoke_llm(text + prompt)
    #  with open("../output.txt", "w") as file:
    #      file.write("")
     return info


