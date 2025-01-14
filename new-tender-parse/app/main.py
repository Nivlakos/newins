from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import psycopg2
import config

# Wait for any of given elements to become visible and return the first (and only at that time) visible element. xpathSelectors is normally separated with | character
def wait_xpath_appear(driver, xpathSelectors, timeout = None):
    if timeout is None:
        timeout = 10
    return WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located((By.XPATH, xpathSelectors)))

def wait_css_appear(driver, cssSelector, timeout = None):
    if timeout is None:
        timeout = 10
    return WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, cssSelector)))

def wait_css_exists(driver, cssSelector, timeout = None):
    if timeout is None:
        timeout = 10
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector)))

# a helper method to wait until element **is clickable** and get it **by CSS** or fail if timed out
def find_clickable_css(driver, css: str, timeout=None):
    if timeout is None:
        timeout = 10
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css)))

# a helper method to wait until element **is clickable** and get it **by XPATH** or fail if timed out
def find_clickable_xpath(driver, xpath: str, timeout=None):
    if timeout is None:
        timeout = 10
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))

# Import entire page by opening tenders one by one
def import_page(driver, conn, requests_cookies):
    wait_css_exists(driver, '.pagination')
    for element in driver.find_elements(By.CSS_SELECTOR, '.tender-row .tender-info a'):
        start_time = time.time()
        #print("------------ BeautifulSoap parser -----------")
        #response = requests.get('https://rostender.info/' + element.get_attribute('href'), cookies=requests_cookies)
        #responseHtml = response.content
        #print(f"GET: {time.time() - start_time} секунд")
        #print(responseHtml)
        #soup = BeautifulSoup(responseHtml, 'html.parser')
        #print("Номер: " + soup.find("div", class_="tender-info-header-number").string)
        #print("От: " + soup.find("div", class_=".tender-info-header-start_date").string)
        #print("Место: " + driver.find_element(By.CSS_SELECTOR, ".tender-body__block.n1 .line-clamp").text)
        #print("Заказчик: " + driver.find_element(By.CSS_SELECTOR, ".tender-body__block.n2 .tender-info__text").text)
        #print("Заголовок: " + driver.find_element(By.CSS_SELECTOR, ".tender-header .line-clamp").text)
        #print(f"Всего: {time.time() - start_time} секунд")

        print("------------ Selenium parser ------------")
        # Switch to the tender window
        element.click()
        driver.switch_to.window(driver.window_handles[1])
        wait_css_exists(driver, '.tender-info-header-number')
        #print("Number: " + driver.find_element(By.CSS_SELECTOR, ".tender-info-header-number").text)
        wait_css_exists(driver, '.tender-info-header-start_date')
        #print("Date: " + driver.find_element(By.CSS_SELECTOR, ".tender-info-header-start_date").text)
        wait_css_exists(driver, '.tender-body__block.n1 .line-clamp')
        #print("Delivery Place: " + driver.find_element(By.CSS_SELECTOR, ".tender-body__block.n1 .line-clamp").text)
        wait_css_exists(driver, '.tender-body__block.n2 .tender-info__text')
        #print("Customer: " + driver.find_element(By.CSS_SELECTOR, ".tender-body__block.n2 .tender-info__text").text)
        wait_css_exists(driver, '.tender-header .line-clamp')
        #print("Header: " + driver.find_element(By.CSS_SELECTOR, ".tender-header .line-clamp").text)
        
        # Save the tender
        cur = conn.cursor()
        with cur:
            cur.execute("INSERT INTO tender (request_id, description, date, number, registration_start_time, registration_end_time, status, start_amount, summary_date, delivery_place, customer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (1, driver.find_element(By.CSS_SELECTOR, ".tender-header .line-clamp").text, driver.find_element(By.CSS_SELECTOR, ".tender-info-header-start_date").text, driver.find_element(By.CSS_SELECTOR, ".tender-info-header-number").text, "", "", 0, 0, "", "", ""))

        # Switch back to the tender list
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print(f"Импортировано за: {time.time() - start_time} секунд")

if __name__ == "__main__":
    # Initialize Selenium Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-background-timer-throttling");
    options.add_argument("--disable-backgrounding-occluded-windows");
    options.add_argument("--disable-breakpad");
    options.add_argument("--disable-component-extensions-with-background-pages");
    options.add_argument("--disable-dev-shm-usage");
    options.add_argument("--disable-extensions");
    options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees");
    options.add_argument("--disable-ipc-flooding-protection");
    options.add_argument("--disable-renderer-backgrounding");
    options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess");
    options.add_argument("--force-color-profile=srgb");
    options.add_argument("--hide-scrollbars");
    options.add_argument("--metrics-recording-only");
    options.add_argument("--mute-audio");
    options.add_argument("--headless");
    options.add_argument("--no-sandbox");
    #options.add_argument(f"--user-data-dir={config.CHROME_USER_DATA_FOLDER}")
    #options.add_argument(f"--profile-directory={config.CHROME_PROFILE_NAME}")
    #driver = webdriver.Chrome(options=options)
    
    options.set_capability('browserless:token', '35c829e7-df4a-48c4-9d1f-f5939b221ae8')
    driver = webdriver.Remote(
        command_executor='http://browserless:3000/webdriver',
        options=options
    )

    # Open Advanced Search page
    driver.get("https://rostender.info/extsearch/advanced")

    # wait until loaded
    wait_css_exists(driver, '.pagination')

    # if Login link is visible, log in
    loginLinkElements = driver.find_elements(By.CLASS_NAME, "header-login__signin")
    if len(loginLinkElements) > 0:
        driver.get("https://rostender.info/login")
        wait_css_appear(driver, "#username")
        driver.find_element(By.ID, "username").send_keys(config.ROSTENDER_USER)
        driver.find_element(By.ID, "password").send_keys(config.ROSTENDER_PASS)
        driver.find_element(By.NAME, "login-button").click()
        # in case login credentials are wrong, the script will fail on the following line in 60 seconds and the micro-service will be restarted (with 'restart: always' in docker-compose.yml)
        wait_css_exists(driver, '.pagination', 60)

    # Pass selenium cookies to requests (for comparing import speed with requests library)
    #cookies = driver.get_cookies()
    #requests_cookies = {}
    #requests_cookies['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15'
    #for c in cookies:
    #    requests_cookies[c['name']] = c['value']

    # Open DB connection
    conn = psycopg2.connect(
        dbname=config.TENDER_DB_NAME,
        user=config.TENDER_DB_USER,
        password=config.TENDER_DB_PASS,
        host=config.TENDER_DB_SERVER,
        port=config.TENDER_DB_PORT
    )
    with conn:

        # Get requests list (region+industry to import data for)
        cur = conn.cursor()
        with cur:
            cur.execute("SELECT region_id, industry_id FROM request order by priority asc, created_timestamp desc;")
            rows = cur.fetchall()
        
        for row in rows:

            # Import first page
            import_page(driver, conn, requests_cookies)

            # If more pages exists, import them one by one
            while len(driver.find_elements(By.CSS_SELECTOR, 'li.last a')) > 0:
                find_clickable_css(driver, 'li.last a').click()
                import_page(driver, conn, requests_cookies)


    #time.sleep(1000)