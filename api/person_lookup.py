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
from .scrape import scrape_website1,clean_body_content
# from scrape import scrape_website1,clean_body_content
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Options
import undetected_chromedriver as uc




os.environ["TAVILY_API_KEY"] = "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"

client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)



def get_company(domain):
    prompt = f"Give me the name of the company name with the domain given {domain}. Just return the the company name and nothing else no explanation to be given.Eg(google.com => Google)"
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    return response.choices[0].message.content

def get_linkedin(company):
    prompt = f"Give me the name of the linkedin profile of the company given {company}. Just return the the company linkedin url and nothing else no explanation to be given.Eg(google => linkedin url)"
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    return response.choices[0].message.content


def get_employees(url):
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")  
    driver =  webdriver.Chrome(options=options)
    try:
        driver.get(url)
        employs = driver.find_element(By.XPATH, "//*[@data-test-id='about-us__size']").text
        print(employs)
    except Exception as e:
        employs = "not found"
        print(f"Error: {e}")
    
    driver.quit()  
    return employs


def no_urls(title,employs,company):
    prompt = f"Give me the possible no.of people that could be possible for the given designition {title} at {company} which has {employs}. Just give me the number and nothing else just number"
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    return response.choices[0].message.content


def get_urls(company,title,n=1):
    search = TavilySearchResults(max_results=n)
    prompt=f"site:linkedin.com/in {title} {company}"
    results=search.invoke(prompt)
    urls = [result["url"] for result in results]
    print(urls)
    return results


    