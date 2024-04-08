import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_experimental_option("detach", True)

# 'AL*', 'BA*', 'BE*', 'BI*', 'BL*', 'BO*', 'BR*', 'BU*', 'CA*', 'CE*', 'CH*', 'CI*', 'CL*', 'CO*', 'CU*', 'DA*', 'DE*', 'DH*', 'DI*', 'DO*', 'DR*', 'DU', 'EB*', 'EC*', 'ED*', 'EG*', 'EI*', 'EL*', 'EN*', 'EP*', 'ER*', 'EU*'

# testing alphabet
alphabets = ['ET*']

for k in range (len(alphabets)):

    # initialize the dictionary for readying to create the dataframe at the end (storing data purpose)
    data = {
        "title": [],
        "education_level" : [],
        "Name": [],
        "Address": [],
        "Date": [],
        "Telefon": [],
        "Email": [],
        "Steuerberaterkammer": []
    }
    df = pd.DataFrame(data)

    # intialize the driver that we are going to use
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)

    # starting the website on the driver
    driver.get("https://steuerberaterverzeichnis.berufs-org.de")

    # Find the search bar and type text into it
    search_bar = driver.find_element(By.ID, "search-text")
    search_text = alphabets[k]
    search_bar.send_keys(search_text)
    search_bar.send_keys((Keys.ENTER))

    # initialize the driver for expanding the dropdown list
    select2_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-select2-id="5"]'))
    )

    # expand the dropdown list for showing those street
    select2_dropdown.click()

    # define the driver for getting the street name
    street_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".select2-results__option"))
    )

    # looping through all streets offering within the according alphabet
    for i in range(len(street_options)):
        # require to define this driver again (since it changes the structure after cleaning the street option)
        street_options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".select2-results__option"))
        )

        street_options[i].click()

        time.sleep(8)

        # for extracting those firm
        buttons = driver.find_elements(By.CLASS_NAME, "link-to-detail")

        # looping through all firm offering within the according street
        for j in range(len(buttons)):
            # have to define this driver again (due to the same reason)
            buttons = driver.find_elements(By.CLASS_NAME, "link-to-detail")

            # click the firm sequentially
            buttons[j].click()

            try:
                title_element = driver.find_element(By.ID, "beruf")
                title = title_element.text
            except NoSuchElementException:
                title = ""

            try:
                education_element = driver.find_element(By.ID, "akademische-grade")
                education = education_element.text
            except NoSuchElementException:
                education = ""

            try:
                name_element = driver.find_element(By.ID, "firmenname")
                name = name_element.text
            except NoSuchElementException:
                name_element = driver.find_element(By.ID, "vorname-and-nachname")
                name = name_element.text

            try:
                address_element = driver.find_element(By.ID, "adresse")
                address = address_element.text
            except NoSuchElementException:
                address = ""

            try:
                date_element = driver.find_element(By.XPATH, '//section[@id="bestelldatum"]//span[@class="text-wrap"]')
                date = date_element.text
            except NoSuchElementException:
                date = ""

            try:
                telefon_element = driver.find_element(By.ID, "telefon")
                telefon_number_element = telefon_element.find_element(By.CLASS_NAME, "text-wrap")
                telefon = telefon_number_element.text
            except NoSuchElementException:
                telefon = ""

            try:
                email_element = driver.find_element(By.ID, "email")
                email_text_element = email_element.find_element(By.CLASS_NAME, "text-wrap")
                email = email_text_element.text
            except NoSuchElementException:
                email = ""

            section_element = driver.find_element(By.ID, "regionalkammerSection")
            span_elements = section_element.find_elements(By.TAG_NAME, "span")
            steuerberaterkammer = span_elements[1].text

            df.loc[len(df.index)] = [title, education, name, address, date, telefon, email, steuerberaterkammer]

            time.sleep(8)

            # clicking the back button (for keep ready selecting the next firm)
            back_button = driver.find_element(By.ID, "back-btn")
            back_button.click()

            # slowdown the scrape speed for avoiding API request limitation being hit (not sure it works or not)
            time.sleep(8)

            print(df)

        # clear the street options (for ready selecting the next street) as click the "x" cross button
        clear_all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.select2-selection__clear"))
        )
        clear_all_button.click()

        time.sleep(8)

        # click the street dropdown button
        select2_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-select2-id="5"]'))
        )
        select2_dropdown.click()

    filename = "web_scrape_{}.csv".format(alphabets[k])
    df.to_csv(filename, index=False)
    driver.quit()
    time.sleep(8)