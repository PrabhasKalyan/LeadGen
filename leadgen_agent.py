from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Options

from scrape import scrape_website,extract_body_content


os.environ["TAVILY_API_KEY"] = "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"

client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)

search = TavilySearchResults(max_results=2)
app=FastAPI()

options = Options()
options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)



def scrape(link):
    driver.get(link)
    driver.implicitly_wait(5)
    elements = driver.find_elements(By.TAG_NAME, "a")  
    other_links=[]
    for other_link in elements:
        other_links.append(other_link.get_attribute("href"))
    return other_links


def get_info(link):
    info = ""
    web_data = extract_body_content(scrape_website(link))
    if web_data:
        info = info +web_data
    else:
        pass
    with open("output.txt", "w") as file:
        file.write(info)


get_info("https://cohesiveapp.notion.site/Cohesive-Overview-9838d6031e9c4b829b589c3ec9d5f784")



