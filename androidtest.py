#!/usr/bin/env python
# -*- coding: utf-8 -*-
#author:myers guo


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from appium import webdriver
import os
import time
from pprint import pprint

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

def FindElementTest():
    desired_capabilities = {
        'platformName': 'Android',
        'platformVersion': '4.4',
        'deviceName': 'Android Emulator',
        'app': PATH('./app/GlobalMiShop.apk'),
        'newCommandTimeout': 240
        }


    driver = webdriver.Remote(
        command_executor='http://localhost:4723/wd/hub',
        desired_capabilities=desired_capabilities
    )
    driver.implicitly_wait(30)
    time.sleep(5);
    try:
        print  driver.get_window_size()['width']
        print driver.get_window_size()['height']
        #left
        driver.swipe(850, 1100, 250, 1100)
        #right,100 900 600 900
        driver.swipe(250,1100,850,1100)
        ele = None
        #向下滑动到底部400 1600 400 300

        for i in range(1,5):
            driver.swipe(400,1600,400,300,500)

        ele = driver.find_element_by_name('More')
        ele.click()
        print driver.contexts

        #
        driver.switch_to.context('WEBVIEW_com.mi.global.shop')

        ele = driver.find_element_by_css_selector(".acc-list.type dd:nth-last-child(1) a")
        ele.click()
        time.sleep(5)
        driver.switch_to.context('NATIVE_APP')
        driver.swipe(400,1600,400,300,500)
        time.sleep(5)


        '''
        for i in range(1):
            #点击购物车
            try:
                ele = driver.find_element(By.ID, 'title_bar_cart_view')
            except:
                ele = None
            if ele is not None:
                ele.click()
            #点击返回
            try:
                ele  = driver.find_element(By.ID,'title_bar_close_btn') #radio_button0
            except:
                ele = None

            if ele is not None:
                ele.click()

            '''
    finally:
        driver.quit()

if __name__ == '__main__':
    try:
        FindElementTest()
    finally:
        print 'end'