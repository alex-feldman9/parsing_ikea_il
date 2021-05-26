# coding: utf-8
import csv
import re
import time
from loguru import logger
from com_funcs import connect, create_csv_file



def create_chapter_link_csv(url, chapter_links_file_name):
    """
    Collect links of site sections (chapters) from main menu
    :param chapter_links_file_name:
    :param url: main web site url
    :return: code of results: Successful result or Fault
    """
    chapter_link_list = []
    driver = connect(url)
    time.sleep(5)
    try:
        popup_close = driver.find_element_by_id('ZA_CANVAS_1248538_CLOSE_X2_3_CONT')
        popup_close.click()
    except:
        pass

    top_bar_menu_button = driver.find_element_by_xpath('//button[@class="navbar-toggle collapsed"]')
    top_bar_menu_button.click()
    # logger.debug(f"top_bar_menu_button found")
    pull_down_products_menu = driver.find_element_by_xpath(
        '(//i[@class="top_menu_pulldown pull-down glyphicon glyphicon-menu-down"])[1]')
    pull_down_products_menu.click()
    # logger.debug(f"pull_down_products_menu found")
    menu_item_links = driver.find_elements_by_xpath(
        '(//ul[@class="menu_products ng-scope"])[position()<=2]/li[@class="item_row ng-scope"]/a')
    # logger.debug(f"menu items found")
    for i in range(len(menu_item_links)):
        time.sleep(3)
        try:
            menu_item_links[i].click()
            # logger.debug(f"menu_item_links {i} click")
        except:
            logger.error(f"can't click on menu_item_links {i}. Try again")
            try:
                time.sleep(3)
                menu_item_links[i].click()
                # logger.debug(f"menu_item_links {i} click second")
            except:
                logger.error(f"Can't click on menu_item_links {i} again. Pass it.")
                return 'Fault'  # error

        chapter_link_list.append(driver.current_url)
        # logger.debug(f"Link: {driver.current_url} added")
        # driver.back()
        top_bar_menu_button = driver.find_element_by_xpath('//button[@class="navbar-toggle collapsed"]')
        time.sleep(3)
        try:
            top_bar_menu_button.click()
        except:
            try:
                time.sleep(3)
                top_bar_menu_button.click()
            except:
                logger.error(f"Can't click on Top menu")
                return 'Fault'  # error
        time.sleep(1)
        pull_down_products_menu = driver.find_element_by_xpath(
            '(//i[@class="top_menu_pulldown pull-down glyphicon glyphicon-menu-down"])[1]')
        try:
            time.sleep(5)
            pull_down_products_menu.click()
        except:
            # logger.error(f"Can't click pull_down_products_menu")
            pass
        menu_item_links = driver.find_elements_by_xpath(
            '(//ul[@class="menu_products ng-scope"])[position()<=2]/li[@class="item_row ng-scope"]/a')
    #    # logger.debug(f"Step {i} pass")
    logger.info(f"The chapter_link_list with {len(chapter_link_list)} items created")

    chapter_links_write_to_csv(chapter_link_list, chapter_links_file_name)
    driver.close()
    return 'Successful result'


def chapter_links_write_to_csv(chapter_link_list, chapter_links_file_name):
    f = open(chapter_links_file_name, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['parse_dt', 'chapter_name', 'chapter_link'])
    for link in chapter_link_list:
        if link == 'https://www.ikea.co.il/kitchens/tour':
            link = 'https://www.ikea.co.il/catalogue/Kitchen'
        link = re.findall(r"\S+catalogue/\w+", link)[0]
        chapter_name = re.split(r"/", link)[-1]
        chapter_name = re.sub(r"_", " ", chapter_name)
        writer.writerow([time.strftime('%Y-%m-%d'), chapter_name, link])
    f.close()


def collect_chapter_links(product_links_tmp_file_name, chapter_links_file_name):
    url = 'https://www.ikea.co.il/'

    # Create chapter links and save it to csv file
    for i in range(2):  # Number of attempts
        logger.info(f"Start create chapter link. Round {i}")
        result_create_chapter_link_csv = create_chapter_link_csv(url, chapter_links_file_name)
        if result_create_chapter_link_csv == 'Successful result':
            logger.info(f"Chapter links csv file created successful")
            # create file for the next luigi's task.
            create_csv_file(file_name=product_links_tmp_file_name,
                            columns_list=['parse_dt', 'chapter_name', 'product_link'])
            break
        elif result_create_chapter_link_csv == 'Fault':
            logger.error(f"Something wrong of create_chapter_link_csv func")
            continue
        else:
            logger.error(f"Unknown error of create_chapter_link_csv func. Try again")
            continue

