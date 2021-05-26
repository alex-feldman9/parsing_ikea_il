#!/usr/bin/env python
# coding: utf-8
import csv
import os
import re
import time
import pandas as pd
from loguru import logger
from com_funcs import connect


def parse_page(page_url, chapter_name):
    """
    The function scrape data from page and send it to write_to_csv function for writing to file
    :param page_url: string of the product page url
    :param chapter_name: string of chapter name
    :return: 'Parsing fault' or 'Product was parsed successfully'
    """
    try:
        driver = connect(page_url)
    except:
        return "Can't open page"

    try:
        item_product_id = driver.find_element_by_xpath('//span[@class="product_code ng-binding"]').text
        item_product_name = driver.find_element_by_xpath('//span[@class="prod_name ng-binding"]').text
        item_product_series = driver.find_element_by_xpath('//span[@class="prod_series ng-binding"]').text
        item_product_color = driver.find_element_by_xpath('//span[@class="prod_color ng-binding"]').text

        try:
            item_special_price = format_price(driver.find_element_by_xpath(
                '//div[@class="price ng-binding special_wrap"]').text)
            item_price = format_price(driver.find_element_by_xpath('//div[contains(@class, "regular_price")]').text)

        except:
            item_special_price = ''
            item_price = format_price(driver.find_element_by_class_name('price').text)

        product_features = {'product_id': item_product_id, 'chapter_name': chapter_name,
                            'product_name': item_product_name,
                            'price': item_price, 'special_price': item_special_price,
                            'product_series': item_product_series,
                            'product_color': item_product_color, 'product_link': page_url}
        # logger.debug(f"Product_features: {product_features}")
        product_write_to_csv(product_features)

        logger.info(f"Product {item_product_id} parsed successfully")
        driver.close()
        return 'Product was parsed successfully'
    except:
        logger.error(f"Parsing fault for page_url: {page_url}")
        driver.close()
        return 'Parsing fault'


def product_write_to_csv(product_features):
    """
    Write dict product_features to csv file
    :param product_features: dict
    :return: nothing
    """
    f = open(parse_products.product_tmp_file_name, 'a', newline='', encoding='utf-8')
    writer = csv.writer(f)

    writer.writerow([time.strftime('%Y-%m-%d'), product_features.get('product_id'),
                     product_features.get('chapter_name'), product_features.get('product_name'),
                     product_features.get('product_series'), product_features.get('product_color'),
                     product_features.get('price'), product_features.get('special_price'),
                     product_features.get('product_link')])
    f.close()
    # logger.debug(f"Info about product_id: {product_features.get('product_id')} is in csv-file")


def format_price(price_value):
    """
    Cleaning price values
    For example: "1,495  ₪" --> 1495
    :param price_value:
    :return: cleaned price value
    """
    price_value = re.sub(r",", "", price_value)
    price_value = re.findall(r"^\d+", price_value)[0]
    return int(price_value)


def broken_link_write_to_csv(broken_link):
    f = open('data/broken_links.csv', 'a', newline='')
    writer = csv.writer(f)
    writer.writerow([time.strftime('%Y-%m-%d'), broken_link])


def next_index_product_links(df, last_product_id):
    for row in df.itertuples():
        product_id = re.findall(r'\d+$', row.product_link)[0]
        if int(product_id) == last_product_id:
            return row.Index
    return -1


def parse_products(product_links_file_name, product_tmp_file_name, products_file_name):
    parse_products.product_tmp_file_name = product_tmp_file_name

    product_link_data = pd.read_csv(product_links_file_name)
    # check that data exist and the script starts after error.
    current_products_tmp = pd.read_csv(product_tmp_file_name)
    if len(current_products_tmp) != 0:  # there is data in the csv
        last_product_id = current_products_tmp.iloc[-1].product_id
        del current_products_tmp  # clear a memory
        # cut link data for continue from the next row.
        next_index = next_index_product_links(product_link_data, last_product_id) + 1
        if next_index != -1:
            product_link_data = product_link_data[next_index:]

    logger.info(f"Start script")
    for row in product_link_data.itertuples():
        result_parse_page = parse_page(row.product_link, row.chapter_name)
        if result_parse_page == 'Parsing fault':
            broken_link_write_to_csv(row.product_link)
            logger.error('Error parsing. Broken link wrote to file')
            continue
        elif result_parse_page == 'Can\'t open page':
            broken_link_write_to_csv(row.product_link)
            logger.error('Error page open. Broken link wrote to file')
            continue
        elif result_parse_page == 'Product was parsed successfully':
            continue
    os.rename(product_tmp_file_name, products_file_name)  # rename result file
    logger.info(f"The script finished.")
