from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import requests
options = Options()
options.add_argument("--headless") 
options.add_argument("--incognito")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--remote-debugging-port=9222')



driver = webdriver.Chrome(options=options)




def scrape_website(website):
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--incognito")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')
    
    try:
        response = requests.get(website)
        # driver = webdriver.Chrome(options=options)
        # driver.get(website)
        soup = BeautifulSoup(response.text, "html.parser")
        html = soup.prettify() 
    except Exception as e:
        return
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
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')  
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(website)
        driver.get(website)
    except Exception as e:
        return
    html = driver.page_source
    with open("output.txt", "w") as file:
        file.write(clean_body_content(html))
    return html



def login():
    driver.get('https://www.linkedin.com/login')
    email = driver.find_element(By.ID, 'username')
    email.send_keys("prabhas.mudhiveti.ecelliitkgp@gmail.com")
    password = driver.find_element(By.ID, 'password')
    password.send_keys("Mpks123%")
    password.submit()
    with open("cookies.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)




def business(website):
    try:
        try:
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
        except:
            print("logging in")
            login()
            
        driver.get(website)
        description=driver.find_element(By.CLASS_NAME,"org-top-card-summary__tagline")
        company_name = driver.find_element(By.TAG_NAME, "h1")
        els = driver.find_elements(By.CLASS_NAME, "org-top-card-summary-info-list__info-item")
        industry = els[0]
        location = els[1]
        followers = els[2]
        company_size = els[3]
        data=[company_name.text,description.text,industry.text,location.text,followers.text,company_size.text]
        return data
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
    
            

def about(website):
    try:
        try:
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
        except:
            print("logging in")
            login()
        driver.get(website+"/about/")
        about_data = driver.find_element(By.ID,"ember54")
        # print(about_data.text)
        return about_data
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
    finally:
        if driver:
            driver.quit() 



def personal(link):
    try:
        driver.get('https://www.linkedin.com/login')
        name = driver.find_element(By.TAG_NAME,"h1").text
        headline = driver.find_element(By.CLASS_NAME,"text-body-medium break-words")
        driver.find_element(By.CLASS_NAME, "inline-show-more-text__button").click()
        about=driver.find_element(By.CLASS_NAME,"display-flex ph5 pv3").text

    except:
        return None