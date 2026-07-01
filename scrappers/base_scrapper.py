from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
class BaseScrapper:
    def __init__(self):
        self.driver = None
    def start_browser(self, attach=False):
        options = Options()
        if attach:
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=options)
        else:
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1280,900")
            options.add_argument("--user-data-dir=/Users/prasangauprety/chrome_debug")
            options.add_argument("--window-size=1920,1080")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        print("Browser started!")
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        
    def quit(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed!")
        