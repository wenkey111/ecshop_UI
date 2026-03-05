from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
import allure
import os
from datetime import datetime
import csv

BASE_URL = "http://localhost"
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "ecshop_logintest_data.csv")

# 读取测试用例
def get_test_data():
    data = []
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"请先创建测试用例文件：{TEST_DATA_PATH}")
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append((
                row["username"],
                row["password"],
                row["expect_code"],
                row["expect_msg"]
            ))
    return data

# 失败时截图
def take_screenshot(driver, case_name):
    dir_path = os.path.join(os.path.dirname(__file__), "ecshop_login_screenshots")
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"login_error_{case_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    driver.save_screenshot(path)
    print(f"错误截图已保存：{path}")
    allure.attach.file(path, name=f"失败截图_{case_name}", attachment_type=allure.attachment_type.PNG)
    return path

@allure.feature("ECShop用户登录模块")
class TestECShopUI:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()
        allure.step("初始化浏览器：打开Chrome并最大化窗口")

    @allure.story("用户登录功能验证")
    @allure.title("登录用例：用户名={0}，密码={1}")
    #@allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("username, password, expect_code, expect_msg", get_test_data())
    def test_login_search_flow(self, username, password, expect_code, expect_msg):
        allure.attach(f"用户名：{username}\n密码：{password}\n预期结果：{expect_msg}", name="测试参数",attachment_type=allure.attachment_type.TEXT)
        try:
            with allure.step("1. 打开ECShop首页"):
                self.driver.get(BASE_URL)
            #定位登录按钮
            with allure.step("2. 点击登录按钮，进入登录页面"):
                login_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "sign"))
                )
                login_btn.click()
            with allure.step("3. 输入用户名和密码"):
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "username"))
                )
                username_input.send_keys(username)
                password_input = self.driver.find_element(By.NAME, "password")
                password_input.send_keys(password)
            with allure.step("4. 点击登录按钮，提交登录请求"):
                submit_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "loginbtn"))
                )
                submit_btn.click()
            with allure.step("5. 验证登录结果"):
                if username and password:
                    text_div=WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//*[@class='boxCenterList RelaArticle']"))
                    )
                    assert expect_msg in text_div.text, f"实际结果：{text_div.text}，预期结果：{expect_msg}"
                else:
                    alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
                    msg = alert.text
                    alert.accept()
                    assert expect_msg in msg, f"实际提示：{msg}，预期提示：{expect_msg}"
        except Exception as e:
            error_info = str(e)
            take_screenshot(self.driver, f"login_{username}")
            allure.attach(error_info, name="错误详情", attachment_type=allure.attachment_type.TEXT)
            # 终止当前用例，不影响其他用例
            pytest.fail(f"用例执行失败：{error_info}", pytrace=False)
    #关闭浏览器
    def teardown_method(self):
        with allure.step("清理环境：关闭浏览器"):
            self.driver.quit()
if __name__ == "__main__":
    # 执行测试并生成Allure报告数据
    pytest.main([__file__, "--alluredir", "./allure-login-results", "-v"])
    # 启动Allure报告服务（执行完代码后，会自动打开浏览器显示报告）
    os.system("allure serve ./allure-results")