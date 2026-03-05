from selenium.webdriver.common.by import By
from UIPO.base.base_page import BasePage

class HomePage(BasePage):
    """首页元素和操作封装"""
    REGISTER_BTN = (By.CLASS_NAME, "reg")       # 注册按钮
    SEARCH_INPUT = (By.NAME, "keywords")        # 搜索框
    SEARCH_BTN = (By.CLASS_NAME, "btn_search") # 搜索按钮
    CART_INFO = (By.ID, "ECS_CARTINFO")         # 购物车悬浮元素

    def click_register_btn(self):
        """点击注册按钮"""
        self.find_clickable_element(self.REGISTER_BTN).click()

    def search_goods(self, search_key: str):
        """搜索商品"""
        search_ele = self.find_element(self.SEARCH_INPUT)
        search_ele.clear()
        search_ele.send_keys(search_key)
        self.find_clickable_element(self.SEARCH_BTN).click()

    def hover_cart(self):
        """鼠标悬浮在购物车"""
        cart_ele = self.find_clickable_element(self.CART_INFO)
        self.driver.execute_script(
            "var evt = document.createEvent('Events');evt.initEvent('mouseover', true, true);arguments[0].dispatchEvent(evt);",
            cart_ele
        )