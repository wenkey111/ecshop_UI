from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
import allure
import time
import os
from datetime import datetime
import csv

BASE_URL = "http://localhost"
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "ecshop_buytest_data.csv")

#读取测试用例
def get_test_data():
    data = []
    if not os.path.exists(TEST_DATA_PATH):
        raise FileNotFoundError(f"请先创建测试用例文件：{TEST_DATA_PATH}")
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append((
                row["case_id"],
                row["goods_desc"],
                row["search_key"],
                row["goods_loc"],
                row["expect_msg"]
            ))
    return data

def take_screenshot(driver, case_id, case_name):
    dir_path = os.path.join(os.path.dirname(__file__), "ecshop_buy_screenshots")
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"buy_error_{case_id}_{case_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    driver.save_screenshot(path)
    print(f"错误截图已保存：{path}")
    allure.attach.file(path, name=f"加购失败截图_{case_name}", attachment_type=allure.attachment_type.PNG)
    return path

@allure.feature("ECShop用户加购模块")
class TestECShopUI:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()
        allure.step("初始化浏览器：打开Chrome并最大化窗口")

    def is_element_exist(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
            return True
        except NoSuchElementException:
            return False

    @allure.story("用户加购功能验证")  # 具体功能点
    @allure.title("加购用例：{case_id}-{goods_desc}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("case_id,goods_desc,search_key,goods_loc,expect_msg", get_test_data())
    def test_buy_flow(self, case_id, goods_desc, search_key, goods_loc, expect_msg):
        allure.attach(
            f"""
            用例ID：{case_id}
            加购类型：{goods_desc}
            搜索关键词：{search_key}
            商品定位：{goods_loc}
            预期结果：{expect_msg}
            """,
            name="测试用例参数",
            attachment_type=allure.attachment_type.TEXT
        )
        try:
            with allure.step("1.打开ECShop首页并完成登录"):
                self.driver.get(BASE_URL)
                #点击登录按钮
                login_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "sign"))
                )
                login_btn.click()
                #输入账号密码
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, "username"))
                )
                username_input.send_keys("test123")
                password_input = self.driver.find_element(By.NAME, "password")
                password_input.send_keys("123456")
                #点击登录提交按钮
                submit_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "loginbtn"))
                )
                submit_btn.click()
                time.sleep(5)
                allure.attach("登录成功，跳转到ECShop首页", name="登录结果", attachment_type=allure.attachment_type.TEXT)
            with allure.step("2.执行商品加购操作"):
                #有搜索关键词
                if search_key:
                    with allure.step(f"情况1.搜索商品{search_key}并加购"):
                        search_input = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.NAME, "keywords"))
                        )
                        search_input.clear()
                        search_input.send_keys(search_key)
                        #点击搜索按钮
                        self.driver.find_element(By.CLASS_NAME, "btn_search").click()
                        #能搜索到
                        if self.is_element_exist("sort"):
                            with allure.step("搜索到商品，执行加购操作"):
                                goal_div=self.driver.find_element(By.CLASS_NAME, "items-gallery")
                                self.driver.execute_script("var evt = document.createEvent('Events');evt.initEvent('mouseover', true, true);arguments[0].dispatchEvent(evt);", goal_div)
                                #点击商品加购
                                buy_first = WebDriverWait(self.driver, 5).until(
                                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".items-btn .f6"))
                                )
                                buy_first.click()
                                first_spediv = WebDriverWait(self.driver, 8).until(
                                    EC.visibility_of_element_located((By.ID, "speDiv"))
                                )
                                #有两种情况：需要选择型号后再次点击加购、不需要则直接断言
                                if goods_desc == "搜索简易商品加购":
                                    assert "添加成功！" in first_spediv.text
                                    allure.attach("加购成功（无需二次加购的简易物品）", name="加购结果",attachment_type=allure.attachment_type.TEXT)
                                else:
                                    #二次加购
                                    with allure.step("需要选择商品型号，执行二次加购"):
                                        buy_second = WebDriverWait(self.driver, 10).until(
                                            EC.visibility_of_element_located((By.CSS_SELECTOR, "#speDiv .f6"))
                                        )
                                        buy_second.click()
                                        #断言
                                        meg_buy = WebDriverWait(self.driver, 10).until(
                                            EC.visibility_of_element_located((By.CLASS_NAME, "conclose"))
                                        )
                                        assert "添加成功！" in meg_buy.text
                                        allure.attach("加购成功（需二次加购的常规物品）", name="加购结果",attachment_type=allure.attachment_type.TEXT)
                        else:
                            #商品不存在断言
                            with allure.step("未搜索到商品，验证提示信息"):
                                meg_no = WebDriverWait(self.driver, 10).until(
                                    EC.visibility_of_element_located((By.CLASS_NAME, "f5"))
                                )
                                assert "无法搜索到您要找的商品！" in meg_no.text
                                allure.attach("未搜索到商品，提示信息验证通过", name="加购结果",attachment_type=allure.attachment_type.TEXT)
                #不搜索，在首页加购
                else:
                    with allure.step("情况2.首页直接加购商品"):
                        #滑动页面
                        self.driver.execute_script("window.scrollTo(0, 800);")
                        #点击商品进入详情页
                        buy_sh=WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "#f0 .cxjitem"))
                        )
                        buy_sh.click()
                        buy_btn = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, goods_loc))
                        )
                        buy_btn.click()
                        #断言
                        msg_buy = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "conclose"))
                        )
                        assert "添加成功！" in msg_buy.text
                        allure.attach("首页直接加购商品成功", name="加购结果",attachment_type=allure.attachment_type.TEXT)

        except Exception as e:
            error_info = str(e)
            allure.attach(error_info, name=f"[{case_id}]{goods_desc} 执行错误详情",attachment_type=allure.attachment_type.TEXT)
            #失败自动截图
            take_screenshot(self.driver, case_id, goods_desc)
            #终止当前用例，不影响其他用例，关闭堆栈信息，报错更简洁
            pytest.fail(f"[{case_id}]{goods_desc} 用例执行失败：{error_info}", pytrace=False)

    def teardown_method(self):
        with allure.step("清理环境：关闭Chrome浏览器"):
            self.driver.quit()