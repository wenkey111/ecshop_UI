from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
import allure
import time
import os
from datetime import datetime
import csv

BASE_URL = "http://localhost"
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "ecshop_order_data.csv")


# 读取测试用例
def get_test_data():
    data = []
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"请先创建测试用例文件：{TEST_DATA_PATH}")
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:  # order_id,province,city,district,consignee,email,address,tel,shipping,payment,expect_msg
            data.append((
                row["order_id"],
                row["province"],
                row["city"],
                row["district"],
                row["consignee"],
                row["address"],
                row["tel"],
                row["shipping"],
                row["payment"],
                row["expect_msg"]
            ))
    return data


def take_screenshot(driver, case_id):
    dir_path = os.path.join(os.path.dirname(__file__), "ecshop_order_screenshots")
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"order_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    driver.save_screenshot(path)
    print(f"截图已保存：{path}")
    allure.attach.file(path, name=f"下单失败截图_{case_id}", attachment_type=allure.attachment_type.PNG)
    return path

@allure.feature("ECShop用户下单模块")
class TestECShopUI:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()
        allure.step("初始化浏览器：打开Chrome并最大化窗口")

    # 元素是否存在
    def is_element_exist(self, class_name):
        with allure.step(f"检查元素是否存在：class_name={class_name}"):
            try:
                self.driver.find_element(By.CLASS_NAME, class_name)
                return True
            except NoSuchElementException:
                return False

    @allure.story("用户下单地址填写验证")
    @allure.title("下单用例：{order_id} - 收货人={consignee}")
    #@allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("order_id,province,city,district,consignee,address,tel,shipping,payment,expect_msg",get_test_data())
    def test_order_flow(self, order_id, province, city, district, consignee, address, tel, shipping, payment,expect_msg):
        allure.attach(
            f"""
            用例ID：{order_id}
            收货地址：{province}-{city}-{district}
            收货人：{consignee}
            详细地址：{address}
            联系电话：{tel}
            预期结果：{expect_msg}
            """,
            name="测试用例参数",
            attachment_type=allure.attachment_type.TEXT
        )
        try:
            with allure.step("1.打开首页并完成登录"):
                self.driver.get(BASE_URL)
                login_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "sign"))
                )
                login_btn.click()
                # 输入账号密码
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "username"))
                )
                username_input.send_keys("xiaomin")
                password_input = self.driver.find_element(By.NAME, "password")
                password_input.send_keys("888888")
                # 点击登录提交按钮
                submit_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "loginbtn"))
                )
                submit_btn.click()
                time.sleep(5)  # 确保跳转到首页
                allure.attach("登录成功，跳转到ECShop首页", name="登录结果", attachment_type=allure.attachment_type.TEXT)
            with allure.step("2.进入购物车并点击结算"):
                # 鼠标悬浮在购物车
                cart_lst = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "ECS_CARTINFO"))
                )
                self.driver.execute_script(
                    "var evt = document.createEvent('Events');evt.initEvent('mouseover', true, true);arguments[0].dispatchEvent(evt);",
                    cart_lst
                )
                order_btn = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "btn"))
                )
                order_btn.click()
                #跳转购物车页面点击结算
                final_input = self.driver.find_element(By.CLASS_NAME, "fd30_checkout")
                final_input.click()
                allure.attach("成功进入结算页面", name="购物车操作结果", attachment_type=allure.attachment_type.TEXT)
            with allure.step("3.填写收货地址信息"):
                if province.strip():
                    with allure.step(f"3.1:选择省份{province}"):
                        pro_select = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "province"))
                        )
                        p_select = Select(pro_select)
                        p_select.select_by_value(province)
                        time.sleep(0.3)
                # 城市
                if city.strip():
                    with allure.step(f"3.2:选择城市{city}"):
                        city_select = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "city"))
                        )
                        c_select = Select(city_select)
                        c_select.select_by_value(city)
                        time.sleep(0.3)
                # 区域
                if district.strip():
                    with allure.step(f"3.3:选择区域{district}"):
                        district_select = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "district")))
                        d_select = Select(district_select)
                        d_select.select_by_value(district)
                # 姓名
                if consignee.strip():
                    with allure.step(f"3.4:输入收货人{consignee}"):
                        name_input = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "consignee"))
                        )
                        name_input.send_keys(consignee)
                # 地址
                if address.strip():
                    with allure.step(f"3.5:输入详细地址{address}"):
                        add_input = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "address"))
                        )
                        add_input.send_keys(address)
                # 电话
                if tel.strip():
                    with allure.step(f"3.6:输入联系电话{tel}"):
                        tel_input = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "tel"))
                        )
                        tel_input.send_keys(tel)
            with allure.step("4.提交地址并验证提示信息"):
                # 点击地址提交按钮
                sub_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "Submit")))
                sub_btn.click()
                WebDriverWait(self.driver, 10).until(lambda d: d.switch_to.alert)
                alert = self.driver.switch_to.alert
                msg = alert.text.strip()
                expected_keywords = [
                    "收货人姓名不能为空",
                    "收货人的详细地址不能为空",
                    "电话不能为空",
                    "请您选择收货人所在省份",
                    "请您选择收货人所在城市",
                    "请您选择收货人所在区域",
                    "电话号码不是有效的号码"
                ]
                failed_keywords = []
                for keyword in expected_keywords:
                    if keyword in expect_msg:
                        if keyword not in msg:
                            failed_keywords.append(keyword)
                assert len(failed_keywords)==0, f"以下预期关键词未在弹窗中找到：{', '.join(failed_keywords)}"
                allure.attach(f"地址提交提示：{msg}", name="断言结果", attachment_type=allure.attachment_type.TEXT)
                alert.accept()

            # #结算
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # sub2_btn = WebDriverWait(self.driver, 10).until(
            #     EC.visibility_of_element_located((By.NAME, "Submit"))
            # )
            # #无配送无支付
            # if not shipping.strip() and not payment.strip():
            #     sub2_btn.click()
            #     WebDriverWait(self.driver, 10).until(lambda d: d.switch_to.alert)
            #     alert_1 = self.driver.switch_to.alert
            #     msg_1 = alert_1.text
            #     if "您必须选择一个配送方式！" in msg_1:
            #         assert "您必须选择一个配送方式！" in msg_1
            #     alert_1.accept()  # 关闭弹窗
            # # 有配送无支付
            # if shipping.strip() and not payment.strip():
            #     yt_radio = WebDriverWait(self.driver, 10).until(
            #         EC.element_to_be_clickable((By.XPATH, "//input[@name='shipping' and @value='45']"))
            #     )
            #     self.driver.execute_script("window.scrollTo(0, 800);")
            #     yt_radio.click()
            #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #     sub2_btn.click()
            #     WebDriverWait(self.driver, 10).until(lambda d: d.switch_to.alert)
            #     alert_2 = self.driver.switch_to.alert
            #     msg_2 = alert_2.text
            #     if "您必须选择一个支付方式！" in msg_2:
            #         assert "您必须选择一个支付方式！" in msg_2
            #     alert_2.accept()  # 关闭弹窗
            # # 有配送有支付 订单成功
            # if shipping.strip() and payment.strip():
            #     yt_radio = WebDriverWait(self.driver, 10).until(
            #         EC.element_to_be_clickable((By.XPATH, "//input[@name='shipping' and @value='45']"))
            #     )
            #     self.driver.execute_script("window.scrollTo(0, 800);")
            #     yt_radio.click()
            #     pay_radio = WebDriverWait(self.driver,10).until(
            #         EC.element_to_be_clickable((By.XPATH, "//input[@name='payment' and @value='3']"))
            #     )
            #     pay_radio.click()
            #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #     sub2_btn.click()
            #     suc_msg = WebDriverWait(self.driver, 10).until(
            #         EC.visibility_of_element_located((By.XPATH, "//h6[contains(text(), '订单已提交成功')]")))
            #     assert "订单已提交成功" in suc_msg.text

        except Exception as e:
            error_info = str(e)
            allure.attach(error_info, name=f"[{order_id}]执行错误详情", attachment_type=allure.attachment_type.TEXT)
            take_screenshot(self.driver, order_id)
            pytest.fail(f"[{order_id}]用例执行失败：{error_info}", pytrace=False)

    def teardown_method(self):
        with allure.step("清理环境：关闭Chrome浏览器"):
            self.driver.quit()