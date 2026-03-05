from selenium import webdriver
import pytest
import allure
import os
import csv
from UIPO.pages.login_page import LoginPage
from UIPO.pages.home_page import HomePage

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "../ecshop_logintest_data.csv")

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
@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(15)
    driver.maximize_window()
    yield driver
    driver.quit()

@allure.feature("ECShop用户登录模块")
class TestECShopLogin:
    @allure.story("用户登录功能验证")
    @allure.title("登录用例：用户名={0}，密码={1}")
    @pytest.mark.parametrize("username, password, expect_code, expect_msg", get_test_data())
    def test_login_flow(self, driver, username, password, expect_code, expect_msg):
        # 初始化页面对象
        home_page = HomePage(driver)
        login_page = LoginPage(driver)

        allure.attach(f"用户名：{username}\n密码：{password}\n预期结果：{expect_msg}",
                      name="测试参数", attachment_type=allure.attachment_type.TEXT)

        try:
            with allure.step("1. 打开ECShop首页"):
                home_page.open()

            with allure.step("2. 执行登录操作"):
                login_page.login(username, password)  # 调用封装的登录方法

            with allure.step("3. 验证登录结果"):
                if username and password:
                    # 调用封装的方法获取提示文本
                    actual_msg = login_page.get_login_success_text()
                    assert expect_msg in actual_msg, f"实际结果：{actual_msg}，预期结果：{expect_msg}"
                else:
                    # 调用封装的弹窗处理方法
                    actual_msg = login_page.switch_to_alert()
                    assert expect_msg in actual_msg, f"实际提示：{actual_msg}，预期提示：{expect_msg}"

        except Exception as e:
            error_info = str(e)
            # 调用封装的截图方法
            login_page.take_screenshot(
                screenshot_dir=os.path.join(os.path.dirname(__file__), "../ecshop_login_screenshots"),
                case_id=f"login_{username}",
                case_name=f"用户名{username}_密码{password}"
            )
            allure.attach(error_info, name="错误详情", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"用例执行失败：{error_info}", pytrace=False)


if __name__ == "__main__":
    pytest.main([__file__, "--alluredir", "./allure-login-results", "-v"])
    os.system("allure serve ./allure-results")