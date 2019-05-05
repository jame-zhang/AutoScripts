#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-05-04 14:06
# @Author  : Jame
# @Site    : 
# @File    : AppleidSiteAction.py
# @Software: PyCharm

import json
import pickle
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium .webdriver.support import expected_conditions as EC
import random


class AppleidSiteAction:
    def __init__(self, file="accounts.json"):
        self.url = "https://appleid.apple.com"
        # chrome_options = ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument(
        #     'user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"')
        # self.browser = webdriver.Chrome(options=chrome_options)
        self.browser = webdriver.Chrome()
        # self.browser.minimize_window()
        self.accounts = None
        self.account = ""
        self.current_password = ""
        self.new_password = ""
        self.file = file
        self.questions = None
        self._web_driver_wait = WebDriverWait(self.browser, 20)
        self.account_key = ""
        self.init_accounts()


    def wait(self, timeout=10, id="", tag_name="", class_name="", xpath=""):
        """
            selenium 继续操作等待函数
        :param timeout: 超时时间，即最大等待时间
        :param id: 查找元素的id，找到了则停止等待
        :param tag_name: 查找元素的标签
        :param class_name: 查找元素的id，找到了则停止等待
        :return:
            id不为空: Fasle, None;
            id为空: Fasle, webElement;
        """
        element = None
        if  id:
            element = self._web_driver_wait.until(EC.presence_of_element_located((By.ID, id)))
        elif  tag_name:
            element = self._web_driver_wait.until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
        elif  class_name:
            element = self._web_driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        elif xpath:
            element = self._web_driver_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element

    def text_fill(self, id, key):
        """
            向指定id发送数据
        :param id:
        :param key:
        :return:
        """
        element = self.wait(id=id)
        element.send_keys(key)

    def button_click_by_id(self, id):
        button = self._web_driver_wait.until(EC.presence_of_element_located((By.ID, id)))
        button.click()

    def button_click_by_contains(self, type, value):
        button = None
        if "id" in type:
            button = self.browser.find_element_by_xpath(("//button[contains(@id,"+value+")]"))
        elif "class" in type:
            button = self.browser.find_element_by_xpath(("//button[contains(@class,"+value+")]"))
        button.click()

    def button_click_by_xpath(self, xpath):
        button = self._web_driver_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        button.click()

    def signin(self, account_idx=0):
        self.get_account(account_idx)
        self.browser.get(self.url)
        iframe_id = self.wait(tag_name='iframe').get_attribute('id')
        self.browser.switch_to.frame(iframe_id)
        self.text_fill("account_name_text_field", self.account)
        self.wait(xpath="//button[(@id='sign-in') and not(contains(@class, 'disable'))]")
        self.button_click_by_id("sign-in")
        time.sleep(1) #元素一直存在，点击之后需要一定时间更改样式，才可以输入，也可以尝试修改div的样式
        self.text_fill("password_text_field", self.current_password)
        self.wait(xpath="//button[(@id='sign-in') and not(contains(@class, 'disable'))]")
        time.sleep(1)
        self.button_click_by_id("sign-in")
        self.wait(class_name='modal-content')
        questions_element = self.browser.find_elements_by_xpath("//div[@class='form-cell']/label")
        questions = [ _.text for _ in questions_element]
        answers = [self.questions[ _] for _ in questions]
        self.wait(class_name="answer")
        ans_elements = self.browser.find_elements_by_class_name("answer")
        for id, ans_input in enumerate(ans_elements):
            ipt = ans_input.find_element_by_tag_name("input")
            ipt.send_keys(answers[id])
        self.browser.find_elements_by_xpath("//div[@class='footer']//button")[1].click()
        print(self.account+"\n    Login success.")

        # self.browser.quit()

    def signout(self):
        self.wait(xpath="//div[not(contains(@class, 'idms-popover-container'))]")
        self.wait(class_name="flex-container-signout")
        btn_signout = self.browser.find_element_by_xpath("//*[@id='managecontent']/manage/div/photo/div/div[2]/div/div/div[2]/div/div/button")
        btn_signout.click()
        print("    Signout success")

    def generate_new_password(self, length=10):
        """
            apple官网要求大写字母和小写字母，至少一个数字，随机密码生成器
        :param length: length必须小于26，英文字符只有26个
        :return:
        """
        alphabet_chars = "-=~!@#$%^&*(()_+,.?[]{}"
        alphabet_capital = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        alphabet_lowercase = "abcdefghijklmnopqrstuvwxyz"
        alphabet_digit = "01234567890"

        # n_capital = random.randint(1,min(length-2,26))
        # n_lowercase = random.randint(1,min(length-1-n_capital, 26))
        # n_digit = random.randint(1, min(length-n_capital-n_lowercase, 10))
        # n_chars = min(length - sum([n_digit, n_capital, n_lowercase]), 23)
        #TODO: 无法解决字符串平衡性问题，chars生成的概率很小
        n_capital = 3
        n_lowercase = 3
        n_digit = 2
        n_chars = 2
        pwd_capital ="".join([alphabet_capital[_] for _ in random.sample(range(0,len(alphabet_capital)),n_capital)])
        pwd_lowercase="".join([alphabet_lowercase[_] for _ in random.sample(range(0,len(alphabet_lowercase)),n_lowercase)])
        pwd_digit="".join([alphabet_digit[_] for _ in random.sample(range(0,len(alphabet_digit)),n_digit)])
        pwd_chars="".join([alphabet_chars[_] for _ in random.sample(range(0,len(alphabet_chars)),n_chars)])
        pwd_list = [pwd_capital, pwd_lowercase, pwd_digit, pwd_chars]
        password = ''.join( pwd_list[_] for _ in random.sample(range(0,4),4))
        self.new_password = password
        print(password)
        return password

    def change_password_after_login(self):
        self.wait(id="managecontent")
        btn_change_password = self.browser.find_element_by_xpath('//*[@id="security-content"]/div[1]/div[1]/div/div/changepassword/div/div/button')
        btn_change_password.click()
        self.wait(class_name="idms-popover-container")
        input_currrent_password = self.browser.find_element_by_xpath("//div[contains(@class, 'current-password')]//input")
        input_currrent_password.send_keys(self.current_password)
        self.new_password = self.generate_new_password()
        input_new_password = self.browser.find_element_by_xpath("//div[contains(@class, 'new-password')]//input")
        input_new_password.send_keys(self.new_password)
        input_confirm_password = self.browser.find_element_by_xpath("//div[contains(@class, 'confirm-password')]//input")
        input_confirm_password.send_keys(self.new_password)
        btn_xpath = "//div[contains(@class, 'idms-step-footer')]//button[contains(@class, 'button-primary') and not(contains(@class, 'disable'))]"
        self.button_click_by_xpath(xpath=btn_xpath)
        update_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.update_account(update_at)
        print("    Password changed success.")

    def change_password_without_login(self):
        pass

    def init_accounts(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            self.accounts = json.load(f)

    def get_account(self, idx=0):
        idx = (idx -1) if idx >= len(self.accounts) else idx
        self.account_key = list(self.accounts.keys())[idx]
        item = self.accounts[self.account_key]
        self.account = item["account"]
        self.current_password= item["current_password"]
        self.questions = item["questions"]

    def update_account(self, update_at=""):
        if self.new_password:
            self.accounts[self.account_key]["current_password"] = self.new_password
            self.accounts[self.account_key]["history"]["old_password"] = self.current_password
            self.accounts[self.account_key]["history"]["update_at"] = update_at
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=4)
        passwords = [self.accounts[key]["account"]+": \n    "+self.accounts[key]["current_password"]+"\n" for key in self.accounts.keys()]
        with open('password.txt', 'w') as f:
            for _ in passwords:
                f.write(_+"\n")



if __name__ == "__main__":
    change = AppleidSiteAction()
    for i in range(len(change.accounts)):
        change.signin(account_idx=i)
        change.change_password_after_login()
        change.signout()
    change.browser.quit()
