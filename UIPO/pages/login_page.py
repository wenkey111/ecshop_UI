from selenium.webdriver.common.by import By
from UIPO.base.base_page import BasePage

class LoginPage(BasePage):
    LOGIN_BTN = (By.CLASS_NAME, "sign")          #登录按钮
    USERNAME_INPUT = (By.NAME, "username")      # 用户名输入框
    PASSWORD_INPUT = (By.NAME, "password")      # 密码输入框
    SUBMIT_BTN = (By.CLASS_NAME, "loginbtn")    # 登录提交按钮
    LOGIN_SUCCESS_MSG = (By.XPATH, "//*[@class='boxCenterList RelaArticle']")  # 登录成功提示

    def click_login_btn(self):
        self.find_clickable_element(self.LOGIN_BTN).click()

    def input_username(self, username: str):
        username_ele = self.find_element(self.USERNAME_INPUT)
        username_ele.clear()
        username_ele.send_keys(username)

    def input_password(self, password: str):
        password_ele = self.find_element(self.PASSWORD_INPUT)
        password_ele.clear()
        password_ele.send_keys(password)

    def click_submit_btn(self):
        self.find_clickable_element(self.SUBMIT_BTN).click()

    def login(self, username: str, password: str):
        self.click_login_btn()
        self.input_username(username)
        self.input_password(password)
        self.click_submit_btn()

    def get_login_success_text(self):
        return self.find_element(self.LOGIN_SUCCESS_MSG).text