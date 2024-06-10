import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.add_experimental_option("detach", True)

def scraping (url, alphabet_list):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    driver.get(url)
    time.sleep(2)
    dropdown = Select(driver.find_element(By.ID, "sucheForm:land"))
    dropdown.select_by_visible_text("Deutschland")
    for alphabet in alphabet_list:
        data = {
            "title": [],
            "education_level": [],
            "kontaktperson": [],
            "Address": [],
            "Date": [],
            "Telefon": [],
            "mobile" :[],
            "Email": [],
            "Fax" : [],
            "Website" : []
        }
        df = pd.DataFrame(data)
        input_box = driver.find_element(By.ID, "sucheForm:name")
        input_box.send_keys(alphabet)
        input_box.send_keys(Keys.ENTER)
        time.sleep(2)
        for i in range(len(driver.find_elements(By.TAG_NAME, "tbody"))):
            tbody = driver.find_elements(By.TAG_NAME, "tbody")[i]
            for j in range(len(driver.find_elements(By.TAG_NAME, "tbody")[i].find_elements(By.TAG_NAME, "tr"))):
                tr = driver.find_elements(By.TAG_NAME, "tbody")[i].find_elements(By.TAG_NAME, "tr")[j]
                try:
                    link = tr.find_element(By.TAG_NAME, "a")
                    link.click()
                    time.sleep(2)
                    try:
                        title_element = driver.find_element(By.CLASS_NAME, "page-title")
                        soup = BeautifulSoup(title_element.get_attribute('innerHTML'), 'html.parser')
                        title = soup.text.split('\n')[0].strip()
                    except NoSuchElementException:
                        title = ""
                    try:
                        address_element = driver.find_element(By.TAG_NAME, "address")
                        address = address_element.text.replace('\n', ' ')
                    except NoSuchElementException:
                        address = ""
                    education = ""
                    date = ""
                    try:
                        title_element = driver.find_element(By.CLASS_NAME, "page-title")
                        next_element = driver.execute_script("return arguments[0].nextElementSibling", title_element)
                        if next_element.tag_name == "ul":
                            li_elements = next_element.find_elements(By.TAG_NAME, "li")
                            li_texts = [li.text for li in li_elements]
                            education = ' '.join(li_texts)
                            date_text = driver.execute_script("return arguments[0].nextSibling.textContent",
                                                              next_element)
                            next_sibling = driver.execute_script("return arguments[0].nextElementSibling", next_element)
                            date_text = next_sibling.text
                            match = re.search(r"\d{2}\.\d{2}\.\d{4}", date_text)
                            if match:
                                date = match.group()
                        else:
                            date_text = driver.execute_script("return arguments[0].nextSibling.textContent",
                                                              title_element)
                            match = re.search(r"\d{2}\.\d{2}\.\d{4}", date_text)
                            if match:
                                date = match.group()
                    except NoSuchElementException:
                        print("No title element found")
                        continue
                    dt_elements = driver.find_elements(By.XPATH, "//dt")
                    dt_texts = [element.text for element in dt_elements]
                    internet_element = driver.find_element(By.XPATH,
                                                           "//dt[text()='Internet']/following-sibling::dd[1]") if 'Internet' in dt_texts else None
                    internet = internet_element.text if internet_element else ""
                    telefon_element = driver.find_element(By.XPATH,
                                                          "//dt[text()='Telefon']/following-sibling::dd[1]") if 'Telefon' in dt_texts else None
                    telefon = telefon_element.text if telefon_element else ""
                    email_element = driver.find_element(By.XPATH,
                                                        "//dt[text()='E-Mail']/following-sibling::dd[1]") if 'E-Mail' in dt_texts else None
                    email = email_element.text if email_element else ""
                    mobil_element = driver.find_element(By.XPATH,
                                                        "//dt[text()='Mobil']/following-sibling::dd[1]") if 'Mobil' in dt_texts else None
                    mobil = mobil_element.text if mobil_element else ""
                    fax_element = driver.find_element(By.XPATH,
                                                      "//dt[text()='Fax']/following-sibling::dd[1]") if 'Fax' in dt_texts else None
                    fax = fax_element.text if fax_element else ""
                    kontaktperson_element = driver.find_element(By.XPATH,
                                                                "//dt[text()='Kontaktperson']/following-sibling::dd[1]") if 'Kontaktperson' in dt_texts else None
                    kontaktperson = kontaktperson_element.text if kontaktperson_element else ""
                    df.loc[len(df.index)] = [title, education, kontaktperson, address, date, telefon, mobil, email, fax, internet]
                    driver.back()
                    time.sleep(2)
                except NoSuchElementException:
                    print("No link found")
                    continue
        df.to_csv(f"web_scrape_{alphabet}.csv", index=False)
        input_box = driver.find_element(By.ID, "sucheForm:name")
        input_box.clear()

# too much of data needs to use workstation to run it
# "GM"

# may edit the alphabet list to scrape the specific alphabet
alphabet_list = ["DU", "FR", "HA", "KO", "MI"]

scraping("https://www.wpk.de/berufsregister/suche.xhtml", alphabet_list)