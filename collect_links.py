#!/usr/bin/env python
# coding: utf-8
import csv
import time
import pandas as pd
from loguru import logger
from com_funcs import connect, create_csv_file


def collect_links_one_page(driver):
    """
    The function collect links from one web page.
    Params: Driver(Selenium object)
    Return: List of product links from the page
    """
    page_product_links = []

    product_list = driver.find_elements_by_class_name('prod_txt')

    for i in range(len(product_list)):
        prod_link = product_list[i].find_element_by_class_name('prod_link')
        page_product_links.append(prod_link.get_attribute("href"))

    return page_product_links



def links_write_to_csv(link_list, chapter_name):
    f = open(collect_product_links.product_links_tmp_file_name, 'a', newline='')
    writer = csv.writer(f)
    for link in link_list:
        writer.writerow([time.strftime('%Y-%m-%d'), chapter_name, link])
    f.close()
    # logger.info(f'Links from page {page} are in {links_file_name} file')


def collect_links_from_chapter(chapter_name, url):
    driver = connect(url)
    try:
        num_pages = driver.find_element_by_xpath(
            '//div[@class="pagination_wrap_desktop"]//li[@class="ng-scope"][last()]/a').text
    except:
        num_pages = 1
    for page in range(1, int(num_pages) + 1):
        logger.debug(f"Start parsing chapter {chapter_name}, page {page} from {num_pages}")
        page_product_links = collect_links_one_page(driver)
        links_write_to_csv(page_product_links, chapter_name)

        if page != int(num_pages):

            next_page_button = driver.find_element_by_xpath(
                    '//div[@class="pagination_wrap_desktop"]//li[@class="directionLinks last ng-scope"]/a/span')
            # logger.debug(f"Next page button for page {page} found successfully")

            driver.execute_script("arguments[0].click();", next_page_button)
            time.sleep(3)

    driver.close()
    logger.info(f"Chapter {chapter_name} collected to file successfully.")


def collect_links_from_site(chapter_data):
    """
    reading row by row chapter data and parsing sections of site
    :param chapter_data:
    :return: result code 'Fault' or 'Successful result',
             current chapter name and current Index of row
    """
    for row in chapter_data.itertuples():
        try:
            collect_links_from_chapter(row.chapter_name, row.chapter_link)
        except:
            logger.error(f"Error of collect_links_from_chapter. Last chapter: {row.chapter_name}")
            return 'Fault', row.chapter_name, row.Index  # error

    logger.info(f"Product links collected from site")
    return 'Successful result', 0  # success


def collect_product_links(product_links_tmp_file_name, chapter_link_file,
                          product_links_file_name, product_tmp_file_name):
    # prepare the product links file

    collect_product_links.product_links_tmp_file_name = product_links_tmp_file_name

    chapter_data = pd.read_csv(chapter_link_file)

    # check that some product links data already exists in df. That means the script starts after error.
    current_product_link_tmp = pd.read_csv(product_links_tmp_file_name)
    if len(current_product_link_tmp) != 0:
        last_chapter_name = current_product_link_tmp.iloc[-1].chapter_name
        del current_product_link_tmp  # clear a memory
        for row in chapter_data.itertuples():
            if row.chapter_name == last_chapter_name:
                chapter_data = chapter_data[row.Index:]
                break

    # Check that chapter data no empty.
    if len(chapter_data) == 0:
        logger.error(f"Chapter data is empty. Try to collect the chapter links first. Script finished")
        exit()
    else:
        logger.info(f"chapter_data has = {len(chapter_data)} links")

    # collect product links from chapters with handle of error
    for i in range(3):  # Number of attempts if error.
        logger.info(f"Start collect links from page. Round {i}")
        result_collect_links_from_site = collect_links_from_site(chapter_data)
        if result_collect_links_from_site[0] == 'Successful result':
            logger.info(f"Collecting links has finished successfully.")
            # drop duplicate and save the resulted file
            product_link_tmp_df = pd.read_csv(product_links_tmp_file_name)
            product_link_tmp_df = product_link_tmp_df.drop_duplicates()
            product_link_tmp_df.to_csv(product_links_file_name, index=False)
            del product_link_tmp_df  # clear a memory

            # make files for the next luigi's task. Make it here because it save data in a case of if the next
            # tasks will be relaunched
            create_csv_file(file_name=product_tmp_file_name, columns_list=['parse_dt', 'product_id', 'chapter_name',
                                                                           'product_name', 'product_series',
                                                                           'product_color',
                                                                           'price', 'special_price', 'product_link'])
            create_csv_file(file_name='data/broken_links.csv', columns_list=['parse_dt', 'broken_link'])

            break
        elif result_collect_links_from_site[0] == 'Fault':
            logger.error(f"Error of collect links. Last chapter: {result_collect_links_from_site[1]}")
            chapter_data = chapter_data[result_collect_links_from_site[2]:]  # cut df
            continue  # try continue from last index

    logger.info(f"The script finished.")
