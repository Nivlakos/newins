#from selenium import webdriver
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By
from playwright.sync_api import sync_playwright
import time
import psycopg2
import config

# Wait for any of given elements to become visible and return the first (and only at that time) visible element. xpathSelectors is normally separated with | character
#def wait_xpath_appear(driver, xpathSelectors, timeout = None):
#    if timeout is None:
#        timeout = 10
#    return WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located((By.XPATH, xpathSelectors)))

#def wait_css_appear(driver, cssSelector, timeout = None):
#    if timeout is None:
#        timeout = 10
#    return WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, cssSelector)))

#def wait_css_exists(driver, cssSelector, timeout = None):
#    if timeout is None:
#        timeout = 10
#    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector)))

# a helper method to wait until element **is clickable** and get it **by CSS** or fail if timed out
#def find_clickable_css(driver, css: str, timeout=None):
#    if timeout is None:
#        timeout = 10
#    return WebDriverWait(driver, timeout).until(
#        EC.element_to_be_clickable((By.CSS_SELECTOR, css)))

# a helper method to wait until element **is clickable** and get it **by XPATH** or fail if timed out
#def find_clickable_xpath(driver, xpath: str, timeout=None):
#    if timeout is None:
#        timeout = 10
#    return WebDriverWait(driver, timeout).until(
#        EC.element_to_be_clickable((By.XPATH, xpath)))

# Import entire page by opening tenders one by one
def import_page(page, conn):
    page.wait_for_selector(".pagination")
    links = page.locator(".tender-row .tender-info a")
    for link, link_index in links:
        print (link.href)
        start_time = time.time()

        print("------------ Selenium parser ------------")
        # Switch to the tender window
        page.click(link)
        page.switch_to(page.pages[1])
        page.wait_for_selector('.tender-info-header-number')
        print("Number: " + page.locator(".tender-info-header-number").text)
        page.wait_for_selector('.tender-info-header-start_date')
        print("Date: " + page.locator(".tender-info-header-start_date").text)
        page.wait_for_selector('.tender-body__block.n1 .line-clamp')
        print("Delivery Place: " + page.locator(".tender-body__block.n1 .line-clamp").text)
        page.wait_for_selector('.tender-body__block.n2 .tender-info__text')
        print("Customer: " + page.locator(".tender-body__block.n2 .tender-info__text").text)
        page.wait_for_selector('.tender-header .line-clamp')
        print("Header: " + page.locator(".tender-header .line-clamp").text)
        
        # Save the tender
        cur = conn.cursor()
        with cur:
            cur.execute("INSERT INTO tender (request_id, description, date, number, registration_start_time, registration_end_time, status, start_amount, summary_date, delivery_place, customer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (1, page.locator(".tender-header .line-clamp").text, page.locator(".tender-info-header-start_date").text, page.locator(".tender-info-header-number").text, "", "", 0, 0, "", "", ""))

        # Switch back to the tender list
        page.pages[1].close()
        page.switch_to.window(page.pages[0])
        print(f"Импортировано за: {time.time() - start_time} секунд")

if __name__ == "__main__":
    
    with sync_playwright() as p:
        
        # Запускаем браузер или подключаемся к browserless/chrome
        if (config.BROWSERLESS_DISABLE):
            browser = p.chromium.launch()
        else:
            browser = p.chromium.connect_over_cdp(f"wss://{config.BROWSERLESS_SERVER}/chromium?token={config.BROWSERLESS_TOKEN}")
        
        with browser.new_context() as context:
            page = context.new_page()
            
            # Открываем расширенный поиск
            page.goto("https://rostender.info/extsearch/advanced", wait_until='domcontentloaded')
            page.wait_for_selector(".pagination")
            
            # Если отображена ссылка для входа, входим в аккаунт
            if (page.is_visible(".header-login__signin")):
                print(f"Вход на rostender.info (username={config.ROSTENDER_USER})...")
                page.goto("https://rostender.info/login")
                page.get_by_role("textbox", name="Логин или E-mail").fill(config.ROSTENDER_USER)
                page.get_by_role("textbox", name="Пароль").fill(config.ROSTENDER_PASS)
                page.get_by_role("button", name="Войти").click()
                page.wait_for_selector('.pagination')
                print("Вошли на rostender.info")
                page.goto("https://rostender.info/extsearch/advanced", wait_until='domcontentloaded')
                page.wait_for_selector(".pagination")
            print("Открыли страницу расширенного поиска")

            # Подключаемся к БД
            conn = psycopg2.connect(
                dbname=config.TENDER_DB_NAME,
                user=config.TENDER_DB_USER,
                password=config.TENDER_DB_PASS,
                host=config.TENDER_DB_SERVER,
                port=config.TENDER_DB_PORT
            )
            with conn:
            
                # Получаем список запросов для парсинга (region+industry)
                cur = conn.cursor()
                with cur:
                    cur.execute("SELECT region_id, industry_id FROM request order by priority asc, created_timestamp desc;")
                    rows = cur.fetchall()

                for row in rows:
                
                    # Import first page
                    import_page(page, conn)

                    # If more pages exists, import them one by one
                    while page.is_visible('li.last a'):
                        page.click('li.last a')
                        import_page(page, conn)


    # Когда все запросы обработаны, ждем 5 минут прежде чем выйти (т.е прежде чем docker compose перезапустит микросервис)
    time.sleep(5*60)