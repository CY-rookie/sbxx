from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import cv2 as cv
import logging
import tkinter.messagebox
import tkinter
import json
from aip import AipOcr
import os
import ddddocr
import logging

LOG_FORMAT = "%(asctime)s : [%(levelname)s] %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
logging.basicConfig(filename='my.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def login(driver):
    url = 'https://sso.stmicroelectronics.cn/User/LoginByPassword'
    driver.get(url)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[1]/ul[2]/form/li[1]/input').send_keys('********')
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[1]/ul[2]/form/li[2]/input').send_keys('********')
    try:
        driver.find_element_by_class_name('an_lan').click()
        return True
    except:
        return False


# 根据待下载文件序号下载文件，当下载成功30个的时候就停止
def download_file(driver, file_url_index=626700, success_count=0):
    file_url_prefix = 'https://www.stmcu.com.cn/Designresource/detail/document/'
    # https://www.stmcu.com.cn/Designresource/detail/datasheet/696144

    file_url = file_url_prefix + str(file_url_index)
    driver.get(file_url)
    sleep(1)

    try:
        driver.find_element_by_id('down_load_btn').click()  # 下载
        return success_count+1
    except:
        # driver.close()
        return success_count


# 读取待下载文件序号
def loadFileUrlIndex(file_path):
    with open(file_path) as index_file:
        file_url_index = index_file.read()
    return int(file_url_index)


# 保存下次要下载的文件序号
def writeFileUrlIndex(file_path, file_url_index):
    with open(file_path, 'w') as index_file:
        index_file.write(str(file_url_index))


def delete_tem_file(filepath):
    files = os.listdir(filepath)
    for file in files:
        if file != 'desktop.ini':
            os.remove(filepath + '\\' + file)


prefs = {'profile.default_content_settings.popups': 2,                  # 设置下载询问窗口，这样可以点击下载按钮，但是不下载文件
         "download.default_directory": "E:\\autoScript\\ST\\trash"}     # 设置文件下载路径
driver = webdriver.Edge(capabilities=prefs)                             # 设置edge的启动参数
driver.get('edge://settings/downloads')
driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div/div[2]/div/div[2]/div[2]/div/div/input").click()


if login(driver) is False:
    # log+邮件通知，登陆失败
    print("failed")
else:
    success = 0
    threshold = 295
    driver.get('https://www.stmcu.com.cn/User/UserCenter')
    old_score = driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[1]/div[2]/p/font").text
    target_score = int(old_score) + threshold
    index_file_path = 'index.txt'
    file_index = loadFileUrlIndex(index_file_path)
    while success < 30:
        success = download_file(driver, file_index, success)
        file_index += 1
    writeFileUrlIndex(index_file_path, file_index)

    # 查看积分是否达到300，不够的话则继续下载
    driver.get('https://www.stmcu.com.cn/User/UserCenter')
    new_score = int(driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[1]/div[2]/p/font").text)
    while new_score < target_score:
        diff = int((target_score - new_score) / 10)
        success = 0
        while success <= diff:
            success = download_file(driver, file_index, success)
            file_index += 1
        writeFileUrlIndex(index_file_path, file_index)
        driver.get('https://www.stmcu.com.cn/User/UserCenter')
        new_score = int(driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[1]/div[2]/p/font").text)

    logging.info("今日分数为: " + str(new_score))
    print(new_score)
    # if new_score == target_score:
    #     logging.info("今日分数为: " + new_score)
    # else:
    #     diff = int((new_score - old_score) / 100)
    #     success = 0
    #     while success < diff:
    #         success = download_file(driver, file_index, success)
    #         file_index += 1
    #     writeFileUrlIndex(index_file_path, file_index)



sleep(2)
driver.get('edge://settings/downloads')
driver.find_element_by_id('search_input').send_keys(Keys.ESCAPE)
sleep(1)
delete_tem_file("C:\\Users\\Administrator\\Downloads")

driver.quit()
