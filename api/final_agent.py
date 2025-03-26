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
from .rag import rag
from .scrape import scrape_website1
from .person_lookup import get_employees
from .main import personal_linkedin

os.environ["TAVILY_API_KEY"] = "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"
client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)



def get_companies(state):
    company = f"{state["messages"][-1].content.prompt} in the following sector {state["messages"][-1].content.sector}"
    search = TavilySearchResults(max_results=5)
    results = search.invoke(company)
    urls = [result["url"] for result in results]
    companies = [url.split(".")[1] for url in urls]
    state={"messages": state["messages"], "companies": companies,"domains":urls}
    return state


def get_summary(state):
    unfiltered_domains = state["domains"]
    purpose = state["messages"][-1].content.prompt
    sector = state["messages"][-1].content.sector
    domains =[]
    for domain in unfiltered_domains:
        scrape_website1(domain)
        with open("output.txt") as f:
            text = f.read()
        prompt = f"Does {domain} actively work on {purpose} in the {sector} industry? Answer strictly 'YES' or 'NO' based on publicly available information."
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
            {"role": "user", "content":prompt}]
            )
        if response.choices[0].message.content == "YES":
            domains.append(domain)
        else:
            pass
    
    companies = [url.split(".")[1] for url in domains]
    state={"messages": state["messages"], "companies": companies,"domains":domains}  
    return state      



def get_linkedin_company(state):
    search = TavilySearchResults(max_results=1)
    linkedin = [search.invoke("site:linkedin.com{company}") for company in state["companies"] ]
    state = {"messages": state["messages"], "linkedin_company": linkedin}
    return state


def employees(state):
    pass

def no_urls(state):
    title = state["messages"][-1].content.title
    companies = [company for company in state["companies"]]
    no_of_employees={}
    for company in companies:
        prompt = f"Give me the possible no.of people that could be possible for the given designition {title} at {company} . Just give me the number and nothing else just number"
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
            {"role": "user", "content":prompt}]
            )
        no_of_employees[company]=response.choices[0].message.content
    state = {"messgaes":state["messgaes"],"no_of_employees":no_of_employees}

def get_urls(state):
    no_of_employees = state["no_of_employees"]
    title = state["messages"][-1].content.title
    data = []
    for employee in no_of_employees:
        search = TavilySearchResults(max_results=employee.value)
        prompt=f"site:linkedin.com/in {title} {employee}"
        results=search.invoke(prompt)
        data.append(results)
    urls =[result["url"] for result in data]
    state = {"messgaes":state["message"],"urls":urls}
    return state

def get_data(state):
    links = state["urls"]
    data =[]
    for link in links:
        info=personal_linkedin(link)
        data.append(info)
    state = {"messgaes":state["message"],"data":data}
    return state





workflow = Graph()
workflow.add_node("get_companies",get_companies)
workflow.add_node("get_summary",get_summary)
workflow.add_node("get_linkedin_company",get_linkedin_company)
workflow.add_node("no_urls",no_urls)
workflow.add_node("get_urls",get_urls)
workflow.add_node("get_data",get_data)

workflow.set_entry_point("get_companies")
workflow.add_edge("get_companies", "get_summary")
workflow.add_edge("get_linkedin_company", "no_urls")
workflow.add_edge("no_urls", "get_urls")
workflow.add_edge("get_urls", "get_data")
workflow.add_edge("get_data", END)
workflow_app=workflow.compile()




def ai_agent(**kwargs):
    prompt =prompt = " ".join(f"{key}: {value}" for key, value in kwargs.items())
    state = {"messages": [HumanMessage(content=prompt)]}
    output = workflow_app.invoke(state)
    return output["data"]



