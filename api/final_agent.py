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
# from .rag import rag
# from .scrape import scrape_website1
# from .person_lookup import get_employees
# from .main import personal_linkedin

from rag import rag
from scrape import scrape_website1,extract_body_content,clean_body_content,scrape_website
from person_lookup import get_employees
# from main import personal_linkedin


os.environ["TAVILY_API_KEY"] = "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"
client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)


def invoke_llm(prompt):
    prompt = prompt  + "\nAnalyze the following query and describe it in 3-4 in breif and give only the answer and nothing else only the answer no explanations strictly"  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    info =response.choices[0].message.content
    return info
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

                **Return `None` for any missing or unavailable data.**  strictly follow this don't give wrong information

                **Format the output as JSON.**  
                """
     with open("output.txt", "w") as file:
        file.write("")
     scrape_website1(link)
     with open("output.txt", "r") as file:
        text=file.read()
     info=invoke_llm(text + prompt)
    #  with open("../output.txt", "w") as file:
    #      file.write("")
     return info


def get_companies(state):
    in_put =  json.loads(state["messages"][-1].content)
    print(in_put)
    company = f'List of the companies in the following sector {in_put["sector"]} related to the {in_put["prompt"]} '
    search = TavilySearchResults(max_results=5)
    results = search.invoke(company)
    urls = [result["url"] for result in results]
    companies = [url.split("/")[2].split(".")[1] for url in urls]
    state={"messages": state["messages"], "companies": companies,"domains":urls}
    print(state)
    return state


def get_summary(state):
    unfiltered_domains = state["domains"]
    in_put =  json.loads(state["messages"][-1].content)
    purpose = in_put["prompt"]
    sector = in_put["sector"]
    domains =[]
    for domain in unfiltered_domains:
        with open("output.txt", "w") as file:
            file.write(clean_body_content(extract_body_content(scrape_website(domain))))
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
    
    companies = [url.split("/")[2].split(".")[1] for url in domains]
    # state={"messages": state["messages"], "companies": companies,"domains":domains}  
    state["companies"] = companies
    state["domains"] = domains
    print(state)
    return state      



def get_linkedin_company(state):
    search = TavilySearchResults(max_results=1)
    linkedin = [result["url"] for company in state["companies"]
                for result in search.invoke(f"site:linkedin.com {company}") ]
    state["linkedin_company"]=linkedin
    print(state)
    return state


def employees(state):
    pass

def no_urls(state):
    in_put =  json.loads(state["messages"][-1].content)
    title = in_put["title"]
    companies = [company for company in state["companies"]]
    no_of_employees={}
    for company in companies:
        prompt = f"Give me the possible no.of people that could be possible for the given designition {title} at {company} . Just give me the number and nothing else just number and exact number linke 5"
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
            {"role": "user", "content":prompt}]
            )
        no_of_employees[company]=response.choices[0].message.content
    state["no_of_employees"]=no_of_employees
    print(state)
    return state

def get_urls(state):
    no_of_employees = state["no_of_employees"]
    in_put =  json.loads(state["messages"][-1].content)
    title = in_put['title']
    data = []
    for key,employee in no_of_employees.items():
        search = TavilySearchResults(max_results=int(employee))
        prompt=f"site:linkedin.com/in {title} {key}"
        results=search.invoke(prompt)
        data.extend(results) 
    urls =[result["url"] for result in data]
    # state = {"messgaes":state["message"],"urls":urls}
    state["urls"]=urls
    print(state)
    return state

def get_data(state):
    links = state["urls"]
    data =[]
    for link in links:
        info=personal_linkedin(link)
        data.append(info)
    # state = {"messgaes":state["message"],"data":data}
    state["data"]=data
    print(state)
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
workflow.add_edge("get_summary", "get_linkedin_company")
workflow.add_edge("get_linkedin_company", "no_urls")
workflow.add_edge("no_urls", "get_urls")
workflow.add_edge("get_urls", "get_data")
workflow.add_edge("get_data", END)
workflow_app=workflow.compile()




def ai_agent(**kwargs):
    # prompt = {key: value for key, value in kwargs.items()}
    prompt = json.dumps(kwargs)
    state = {"messages": [HumanMessage(content=prompt)]}
    output = workflow_app.invoke(state)
    return output["data"]



ai_agent(title="Founder",prompt="Hiring interns",sector="AI India")