from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import allure

class BasePage:
    BASE_URL = "http://localhost"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # 通用元素定位（显式等待）
    def find_element(self, locator: tuple, timeout=10):

        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def find_clickable_element(self, locator: tuple, timeout=10):

        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    # 元素是否存在
    def is_element_exist(self, locator: tuple):
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    # 通用截图方法
    def take_screenshot(self, screenshot_dir: str, case_id: str, case_name: str):

        os.makedirs(screenshot_dir, exist_ok=True)
        file_name = f"{case_id}_{case_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(screenshot_dir, file_name)
        self.driver.save_screenshot(path)
        print(f"截图已保存：{path}")
        allure.attach.file(path, name=f"失败截图_{case_name}", attachment_type=allure.attachment_type.PNG)
        return path

    # 打开页面
    def open(self, url: str = None):
        if url:
            self.driver.get(url)
        else:
            self.driver.get(self.BASE_URL)

    # 处理alert弹窗
    def switch_to_alert(self, timeout=10):
        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        msg = alert.text.strip()
        alert.accept()
        return msg