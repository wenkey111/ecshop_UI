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
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "ecshop_register_data.csv")

# 读取测试用例
def get_test_data():
    data = []
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"请先创建测试用例文件：{TEST_DATA_PATH}")
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append((
                row["reg_id"],
                row["username"],
                row["email"],
                row["password"],
                row["confirm_password"],
                row["extend_field5"],
                row["agreement"],
                row["expect_msg"]
            ))
    return data

# 失败时截图
def take_screenshot(driver, case_name):
    dir_path = os.path.join(os.path.dirname(__file__), "ecshop_register_screenshots")
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"register_error_{case_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    driver.save_screenshot(path)
    print(f"错误截图已保存：{path}")
    allure.attach.file(path, name=f"注册失败截图_{case_name}", attachment_type=allure.attachment_type.PNG)
    return path

@allure.feature("ECShop用户注册模块")
class TestECShopUI:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()
        allure.step("初始化浏览器：打开Chrome并最大化窗口")

    @allure.story("用户注册功能验证")  # 具体功能点
    @allure.title("注册用例：用户名={1}，邮箱={2}，密码={3}")
    #@allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("reg_id,username,email,password,confirm_password,extend_field5,agreement,expect_msg", get_test_data())
    def test_register_flow(self, reg_id,username,email,password,confirm_password,extend_field5,agreement,expect_msg):
        allure.attach(
            f"""
            用例ID：{reg_id}
            用户名：{username}
            邮箱：{email}
            密码：{password}
            确认密码：{confirm_password}
            手机号：{extend_field5}
            同意协议：{agreement}
            预期结果：{expect_msg}
            """,
            name="测试用例参数",
            attachment_type=allure.attachment_type.TEXT
        )
        try:
            with allure.step("1.打开ECShop首页并点击注册按钮"):
                self.driver.get(BASE_URL)
                #注册按钮
                register_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "reg"))
                )
                register_btn.click()
            with allure.step("2.输入用户名并验证用户名合法性"):
                #输入用户名
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "username"))
                )
                username_input.send_keys(username)
                email_input = self.driver.find_element(By.NAME, "email")
                email_input.click()
                #点击后查看用户名提示
                user_notice= WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "username_notice"))
                )
                if username != "xiaoAn":
                    assert expect_msg in user_notice.text, f"实际提示：{user_notice.text}，预期：{expect_msg}"
                    allure.attach(user_notice.text, name="用户名校验结果", attachment_type=allure.attachment_type.TEXT)
                    return
            with allure.step("3.输入邮箱并验证邮箱合法性"):
                email_input.send_keys(email)
                password_input = self.driver.find_element(By.NAME, "password")
                password_input.click()
                email_notice= WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "email_notice"))
                )
                if email != "133@qq.com":
                    assert expect_msg in email_notice.text, f"实际提示：{email_notice.text}，预期：{expect_msg}"
                    allure.attach(email_notice.text, name="邮箱校验结果", attachment_type=allure.attachment_type.TEXT)
                    return
            with allure.step("4.输入密码并验证密码合法性"):
                password_input.send_keys(password)
                conpass_btn = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "confirm_password"))
                )
                conpass_btn.click()
                pass_notice= WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "password_notice"))
                )
                if password != "111111":
                    assert expect_msg in pass_notice.text, f"实际提示：{pass_notice.text}，预期：{expect_msg}"
                    allure.attach(pass_notice.text, name="密码校验结果", attachment_type=allure.attachment_type.TEXT)
                    return
            with allure.step("5.输入确认密码并验证一致性"):
                conpass_btn.send_keys(confirm_password)
                phone_btn = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "extend_field5"))
                )
                phone_btn.click()
                conpass_notice= WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "conform_password_notice"))
                )
                if confirm_password != "111111":
                    assert expect_msg in conpass_notice.text, f"实际提示：{conpass_notice.text}，预期：{expect_msg}"
                    allure.attach(conpass_notice.text, name="确认密码校验结果",attachment_type=allure.attachment_type.TEXT)
                    return
            with allure.step("6.输入手机号并提交注册"):
                reg_btn= WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "Submit"))
                )
                if not extend_field5:
                    reg_btn.click()
                    alert=WebDriverWait(self.driver, 5).until(lambda d: d.switch_to.alert)
                    msg=alert.text
                    alert.accept()
                    assert expect_msg in msg, f"实际提示：{msg}，预期：{expect_msg}"
                    allure.attach(msg, name="手机号校验结果（弹窗）", attachment_type=allure.attachment_type.TEXT)
                    return
                else:
                    phone_btn.send_keys(extend_field5)
                    reg_btn.click()
                    no_msg=WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//*[@class='boxCenterList RelaArticle']"))
                    )
                    if len(extend_field5) != 11:
                        assert expect_msg in no_msg.text, f"实际提示：{no_msg.text}，预期：{expect_msg}"
                        allure.attach(no_msg.text, name="注册结果", attachment_type=allure.attachment_type.TEXT)
                        return
                    assert f"用户名 {username} 注册成功！\n返回上一页\n查看我的个人信息" in no_msg.text
                    allure.attach(no_msg.text, name="注册成功结果", attachment_type=allure.attachment_type.TEXT)

        except Exception as e:
            error_info = str(e)
            allure.attach(error_info, name="用例执行错误详情", attachment_type=allure.attachment_type.TEXT)
            take_screenshot(self.driver, f"{reg_id}")
            pytest.fail(f"用例执行失败：{error_info}", pytrace=False)
    #关闭浏览器
    def teardown_method(self):
        with allure.step("清理环境：关闭Chrome浏览器"):  # 拆分teardown步骤到报告
            self.driver.quit()