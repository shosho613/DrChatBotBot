import datetime
import logging
import azure.functions as func
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
import os
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


CHAT_BOT_URL = "https://healthlab.urmc.rochester.edu/UniversityHealthScreen"
EMAIL = "shohami.sh@gmail.com"

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    return driver

def fill_chat(driver):
    driver.get(CHAT_BOT_URL)
    username = driver.find_element_by_name("Username")
    username.clear()
    username.send_keys(os.environ['NETID_USERNAME'])
    password = driver.find_element_by_name("Password")
    password.send_keys(os.environ['NETID_PASSWORD'])
    password.send_keys(Keys.RETURN)
    time.sleep(1)
    try:
        yes_button = driver.find_element_by_id("NoAnswer")
        for i in range(3):
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "NoAnswer")
                )).click()
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ConfirmNoSymptoms"]/div[3]/div[2]')
          )).click()
    except Exception as e:
        logging.info(e)
        logging.info("Failed at finding elements")
        return "Failed"

    content = ""
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="NegativeScreen"]/div[2]/div[2]/div')
            ))
        content = element.text
    except TimeoutException:
        content = "success"
        logging.info("Could not locate success element")
    
    return content
    
    
def send_email(content):
    message = MIMEMultipart()
    message["From"] = EMAIL
    message["To"] = EMAIL
    message["Subject"] = "ChatBot Scripts Result"
    message.attach(MIMEText(content, "plain"))

    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL, os.environ['EMAIL_PASSWORD'])
        server.sendmail(EMAIL, EMAIL, text)
    

def run():
    content = fill_chat(create_driver())
    send_email(content)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    logging.info("Preparing to do chatbot.")
    run()
    if mytimer.past_due:
        logging.info('The timer is past due!')#

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

