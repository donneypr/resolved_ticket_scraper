import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time

load_dotenv()

current_directory = os.getcwd()
chromedriver_path = os.path.join(current_directory, "chromedriver")
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service)

driver.get("https://ask2lit.lassonde.yorku.ca/app/itdesk/ui/requests")

time.sleep(10)

email = os.getenv("LOGIN_EMAIL")
password = os.getenv("LOGIN_PASSWORD")

email_input = driver.find_element(By.ID, "login_id")
email_input.send_keys(email)

button = driver.find_element(By.ID, "nextbtn")
button.click()

time.sleep(10)
password_field = driver.find_element(By.ID, "password")
password_field.send_keys(password)
button = driver.find_element(By.ID, "nextbtn")
button.click()

time.sleep(10)

def scrape_ticket_details():
    try:
        subject = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='details_inner_title']/div[3]/h1"))
        ).text

        ticket_number = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='rhs_inner_panel']/div[1]/table/tbody/tr[1]/td[2]/span"))
        ).text

        resolution_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='details_inner_view']/div/div/div/div/div[1]/div/div[3]/span/div[1]"))
        )
        resolution_text = resolution_element.text

        print(f"Scraped Subject: {subject}")
        print(f"Scraped Ticket Number: {ticket_number}")
        print(f"Scraped Resolution: {resolution_text}")

        return ticket_number, subject, resolution_text

    except Exception as e:
        print(f"Error scraping ticket details: {e}")
        return None, None, None

def click_if_resolved_ticket(row_idx):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//tr[@row-idx='{row_idx}']"))
        )

        ticket_row = driver.find_element(By.XPATH, f"//tr[@row-idx='{row_idx}']")
        
        try:
            status_field = ticket_row.find_element(By.XPATH, ".//td[contains(@title, 'Resolved')]")
            print(f"Ticket at row-idx={row_idx} is resolved.")
        except:
            print(f"Ticket at row-idx={row_idx} is not resolved.")
            return False
        
        ticket_link = ticket_row.find_element(By.XPATH, ".//span[@class='listview-display-id']")
        ticket_link.click()

        print(f"Clicked on the resolved ticket with row-idx={row_idx}")
        return True

    except Exception as e:
        print(f"Error clicking on the ticket with row-idx={row_idx}: {e}")
        return False

def click_resolution_tab():
    try:
        resolution_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@title='Resolution']"))
        )
        resolution_tab.click()
        print("Clicked on the 'Resolution' tab.")

    except Exception as e:
        print(f"Error clicking on the 'Resolution' tab: {e}")

def click_back_button():
    try:
        back_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='menufixed']/div/div[1]/div/button[1]"))
        )
        back_button.click()
        print("Clicked the 'Back' button to return to the ticket list.")

    except Exception as e:
        print(f"Error clicking on the 'Back' button: {e}")

def click_next_page():
    try:
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-sdp-table-id='pagenav-next']"))
        )
        next_page_button.click()
        print("Clicked the 'Next Page' button.")

        time.sleep(5)

    except Exception as e:
        print(f"Error clicking on the 'Next Page' button: {e}")

def process_resolved_tickets(pages_to_scrape):
    with open('resolved_tickets.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Ticket Number', 'Subject', 'Resolution'])

        for page in range(pages_to_scrape):
            print(f"Processing page {page + 1} of {pages_to_scrape}")
            for row_idx in range(100):
                if click_if_resolved_ticket(row_idx):
                    click_resolution_tab()
                    ticket_number, subject, resolution = scrape_ticket_details()
                    if ticket_number and subject and resolution:
                        writer.writerow([ticket_number, subject, resolution])
                        print(f"Data saved for ticket: {ticket_number}, {subject}, {resolution}")
                    click_back_button()
                    time.sleep(3)

            click_next_page()

pages_to_scrape = 632

process_resolved_tickets(pages_to_scrape)

driver.quit()
