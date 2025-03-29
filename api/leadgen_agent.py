from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Options

from .scrape import scrape_website,extract_body_content,clean_body_content
from urllib.parse import urljoin
# from scrape import scrape_website,extract_body_content,clean_body_content
import requests
from bs4 import BeautifulSoup

os.environ["TAVILY_API_KEY"] = "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"

client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)

search = TavilySearchResults(max_results=2)
app=FastAPI()

# options = Options()
# options.add_argument("--headless") 
# driver = webdriver.Chrome(options=options)



def scrape(link,query):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all("a")
    other_links=[]
    for ele in elements:
        text = ele.get_text().strip()
        if not ele.get("href"):
            continue
        prompt = f"This is the text inside the anchortag analyse the text and tell me if it is usful to answer the query if it may have any useful info in the respective link.Link:{text} and query:{query}. If yes I scrape the particular link and analyse the data so dont hesitate to say no as it saves a lot of time. Answer only Yes or No no further explanations requiered in strict"
        response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
        {"role": "user", "content":prompt}]
        )
        if response.choices[0].message.content=="Yes":
            url = urljoin(link, ele.get("href"))
            other_links.append(url)
            
    return other_links





def get_info(link,query):
    info = ""
    links=scrape(link,query)
    print(links)
    web_data = clean_body_content(extract_body_content(scrape_website(link)))
    info = info +web_data
    for lin in links :
        web_data = clean_body_content(extract_body_content(scrape_website(lin)))
        if web_data:
            info = info +web_data
    with open("output.txt", "w") as file:
        file.write(info)







