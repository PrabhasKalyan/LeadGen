from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Options
import undetected_chromedriver as uc


def scrape_website(website):
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(website)
    except Exception as e:
        return
    html = driver.page_source
    return html




def extract_body_content(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        body_content = soup.body
        if body_content:
            return str(body_content)
    except:
        return



def clean_body_content(body_content):
    try:
        soup = BeautifulSoup(body_content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        return cleaned_content
    except:
        return



def scrape_website1(website):
    options = ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless")  
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(website)
    except Exception as e:
        return
    html = driver.page_source
    with open("output.txt", "w") as file:
        file.write(clean_body_content(html))
    return html


