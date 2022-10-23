import selenium
import selenium.webdriver.firefox.webdriver
from selenium.webdriver.firefox.options import Options

from src.helpers.abstract_classes.SeleniumResourceObtainer import SeleniumResourceObtainer


class FirefoxSeleniumResourceObtainer(SeleniumResourceObtainer):
    __DRIVER_PATH = '/home/petru/Licenta/geckodriver'

    def __init__(self):
        options = Options()
        options.headless = True
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--incognito')
        driver = selenium.webdriver.Firefox(executable_path=self.__DRIVER_PATH, options=options)
        super().__init__(driver)
