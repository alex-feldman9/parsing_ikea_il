#!/usr/bin/env python
# coding: utf-8
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from loguru import logger
from sys import platform


def connect(url):
    """
    Connect to web page.
    :param url: link to web page
    :return: chrome driver object
    """
    if platform == 'linux':
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    elif platform == 'win32':
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # for debugging need comment it ###
        driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        connect.url = url
        body = driver.find_element_by_tag_name('body')
        body.send_keys(Keys.END)
        time.sleep(1)
        # logger.debug(f'Driver {url} created successfully')
    except:
        logger.debug('New connection try')
        try:
            time.sleep(5)
            driver.get(url)
        except:
            logger.error("Can't open web page:", url)

    return driver


def create_csv_file(file_name, columns_list):
    f = open(file_name, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(columns_list)
    f.close()
