import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Driver:
	def __init__(self):
		options = Options()
		options.add_argument('--no-sandbox')
		options.add_argument('--headless')
		options.add_argument("--disable-dev-shm-usage")
		options.add_argument("--disable-gpu")
		options.add_argument("--disable-dev-tools")
		options.add_argument("--no-zygote")
		options.add_argument("--single-process")
		options.add_argument("--remote-debugging-port=9222")
		options.add_experimental_option('extensionLoadTimeout', 60000)
		options.add_argument(
			'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
		)
		self.__driver = webdriver.Chrome(options=options)

	def get(self, url: str) -> 'Driver':
		self.__driver.get(url)
		return self

	def remove_popups(self) -> 'Driver':
		self.__driver.execute_script('''
			for (const b of document.querySelectorAll("button")) {
				if (b.className.includes("close")) b.click();
			}
		''')
		return self.wait()

	def find_element(self, xpath: str) -> WebElement:
		return self.__driver.find_element(By.XPATH, xpath)

	def find_elements(self, xpath: str) -> List[WebElement]:
		return self.__driver.find_elements(By.XPATH, xpath)

	@property
	def page_source(self) -> str:
		return self.__driver.page_source

	def wait(self) -> 'Driver':
		time.sleep(.5)
		return self
