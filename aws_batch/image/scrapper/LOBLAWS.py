import os
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from scrapper.SCRAPPER import STORESCRAPPER
from dataclasses import dataclass, field
import pytz

@dataclass
class LOBLAWSSCRAPPER(STORESCRAPPER):
    df: pd.DataFrame = field(init=False)
    event_num: int = int(os.environ['EVENT_NUM'])
    store_name = 'Loblaws'

    def __post_init__(self):
        self.df = pd.DataFrame({
            'date': [],
            'category': [],
            'sub_category': [],
            'prd_name': [],
            'prd_brand': [],
            'prd_price': [],
            'prd_per_price': [],
            'prd_discount': [],
            'prd_link': [],
            'prd_img': []}
        )
        self.store_name = 'Loblaws'
        self.initialize_web_drive()

    #No need to be called if not using undetected web driver
    def accept_cookie(self):
        for i in range(10):
            try:
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="privacy-policy"]/div/div/button')
                    )
                ).click()
            except Exception as e:
                print('Retrying see if there is term of use')
                time.sleep(5)

    def scrap_main(self):
        """
        The function scrap_main is used to scrape data from a website, navigate through categories and
        subcategories, and save the scraped data to a CSV file.
        """

        self.drive.get(self.params.get('scrapping_websites', None).get(self.store_name, None))
        time.sleep(30)
        #self.accept_cookie()

        for cat in self.scroll_to_category():
            #entry to sub cat page
            cat.click()
            self.head_to_sub_cat()
        try:
            self.df.to_csv(self.output_filepath, index=False)
        except Exception as e:
            print('Error occurs when writing csv file.')
            raise Exception(e)

    def scroll_to_category(self):
        """
        The function `scroll_to_category` scrolls to a specific category on a webpage and returns the
        element corresponding to that category.
        """
        for re_time in range(15):
            #wait for the category list show up and click
            current_url = self.drive.current_url
            try:
                self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="site-layout"]/div[1]/div[3]/div/header/div[2]/div[1]/nav/ul/li[1]/button')
                    )
                ).click()
                break
            except TimeoutException:
                print('Retrying locating the category list...')
                self.drive.get(current_url)
                time.sleep(15)
                #self.accept_cookie()
            except WebDriverException:
                self.reinitialize_web_drive(current_url)
        for i in range(self.event_num, self.event_num+1):
            yield self.drive.find_element(By.XPATH, f'//*[@id="site-layout"]/div[1]/div[3]/div/header/div[2]/div[1]/nav/ul/li[1]/ul/li[{i}]/a')

    def head_to_sub_cat(self):
        """
        The `head_to_sub_cat` function navigates through different subcategories and sub-subcategories on a
        website, scraping data from each page.
        """
        # Getting sub cat name
        current_url = self.drive.current_url
        for re_time in range(15):
            try:
                #wait until the left column shows up
                sub_cat_name = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, 'chakra-heading.css-zmvp7m')
                    )
                ).text
                break
            except TimeoutException:
                print('Retrying locating the sub cat name...')
                self.drive.get(current_url)
                time.sleep(15)
                #self.accept_cookie()
            except WebDriverException:
                self.reinitialize_web_drive(current_url)
        print(f'Scrapping {sub_cat_name}')
        for re_time in range(15):
            try:
                all_sub_cat_sect = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="site-content"]/div/div')
                    )
                )
                break
            except TimeoutException:
                print('Retrying locating the left column sub category list...')
                self.drive.get(current_url)
                time.sleep(15)
                #self.accept_cookie()
            except WebDriverException:
                self.reinitialize_web_drive(current_url)
        root_link = 'https://www.loblaws.ca'
        shop_all_sections = BeautifulSoup(all_sub_cat_sect.get_attribute('innerHTML'), "html.parser")
        shop_all_link_list = shop_all_sections.find_all('a', attrs={"data-testid": 'nav-list-link'})
        #Get all the sub sub cat links
        shop_all_link_list = [root_link + link['href'] for link in shop_all_link_list if link.text == 'See All']
        for shop_all in shop_all_link_list:
            try:
                self.drive.get(shop_all)
            except WebDriverException:
                print('Re initializing the web driver...')
                time.sleep(15)
                self.initialize_web_drive()
                time.sleep(15)
                self.drive.get(shop_all)
                time.sleep(15)
                #self.accept_cookie()
            for re_time in range(15):
                try:
                    sub_sub_cat_name = self.wait.until(
                        EC.visibility_of_element_located(
                            (By.CLASS_NAME, 'chakra-heading.css-zmvp7m')
                        )
                    ).text
                    break
                except TimeoutException:
                    print('Retrying locating to the sub sub cat name...')
                    self.drive.get(shop_all)
                    time.sleep(15)
                    #self.accept_cookie()
                except WebDriverException:
                    self.reinitialize_web_drive(shop_all)
            print(f'Scrapping {sub_sub_cat_name}')
            try:
                page_ele = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="site-content"]/div/div/div[2]/div[7]/nav')
                    )
                )
                page_ele = BeautifulSoup(page_ele.get_attribute('innerHTML'), "html.parser")
                #Find all the possible pages
                total_pg_num = len(page_ele.find_all('button')) - 2
                root_url = self.drive.current_url
                all_sub_sub_pages_url = [root_url + f'?page={i}' for i in range(1, total_pg_num + 1)]
            except:
                #The sub sub cat only have one page
                all_sub_sub_pages_url = [self.drive.current_url]
            self.get_all_items(all_sub_sub_pages_url, sub_cat_name, sub_sub_cat_name)

    def get_all_items(self, sub_sub_pages_url: list, sub_cat_name: str, sub_sub_cat_name: str):
        """
        The function `get_all_items` downloads the content of multiple web pages and returns a list of
        BeautifulSoup objects representing the HTML content of each page.

        :param sub_sub_pages_url: A list of URLs for sub-sub pages. These are the pages that contain the
        items you want to scrape
        :type sub_sub_pages_url: list
        :param sub_cat_name: The `sub_cat_name` parameter is a string that represents the name of a
        sub-category
        :type sub_cat_name: str
        :param sub_sub_cat_name: The `sub_sub_cat_name` parameter is a string that represents the name of a
        sub-sub-category. It is used as a reference to identify and categorize items within that
        sub-sub-category
        :type sub_sub_cat_name: str
        :return: The function `get_all_items` returns a list of BeautifulSoup objects, `all_sub_sub_soup`.
        """
        def download_all_page_content():
            all_sub_sub_soup = []
            for link in sub_sub_pages_url:
                for re_time in range(15):
                    try:
                        self.drive.get(link)
                        break
                    except WebDriverException:
                        self.reinitialize_web_drive(link, 20)
                if re_time >= 14:
                    raise Exception("Loading page exceeded retry limit.")
                for re_time in range(15):
                    try:
                        no_item = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.CLASS_NAME, 'chakra-text.css-29j2bl')
                            )
                        ).text
                        if no_item != 'No items are available.':
                            temp = self.wait.until(
                                EC.visibility_of_element_located(
                                    (By.CLASS_NAME, 'css-c33bww')
                                )
                            )
                            item_list = temp.find_elements(By.CLASS_NAME, 'chakra-linkbox.css-wsykbb')
                            for item in item_list:
                                all_sub_sub_soup.append(BeautifulSoup(item.get_attribute('innerHTML'), "html.parser"))
                            break
                        print('No item available')
                        break
                    except TimeoutException:
                        print('Retrying getting all items...')
                        self.drive.get(link)
                        time.sleep(15)
                        #self.accept_cookie()
                    except WebDriverException:
                        self.reinitialize_web_drive(link, 30)
                if re_time >= 14:
                    raise Exception("Download content exceeded retry limit.")
            return all_sub_sub_soup

        def scrap_item_details(item):
            """
            The function `scrap_item_details` scrapes details of an item from a website and returns a dictionary
            containing the item's information.

            :param item: The `item` parameter is an HTML element that represents a specific item on a webpage.
            The function `scrap_item_details` extracts various details from this item, such as the product name,
            brand, price, discount, link, and image. It then returns a dictionary containing these details
            :return: The function `scrap_item_details` returns a dictionary `prd_item` containing the scraped
            details of an item.
            """
            root_link = 'https://www.loblaws.ca'
            prd_item = dict()
            toronto_tz = pytz.timezone("America/Toronto")
            prd_item['date'] = datetime.now(toronto_tz).strftime('%Y-%m-%d')
            prd_item['category'] = sub_cat_name
            prd_item['sub_category'] = sub_sub_cat_name
            prd_item['prd_name'] = item.find(class_='chakra-heading css-7nn9tu').text
            try:
                prd_brand = item.find(class_='chakra-text css-18dxtfe').text
            except Exception as e:
                prd_brand = None
            prd_item['prd_brand'] = prd_brand
            try:
                prd_price = item.find(class_='chakra-text css-150rkla').text
            except Exception as e:
                prd_price = item.find(class_='chakra-text css-1shm0cj').text
            prd_item['prd_price'] = prd_price
            prd_item['prd_per_price'] = item.find(class_='chakra-text css-8jdluo').text
            try:
                prd_discount = item.find(class_='chakra-text css-1x7try2').text
            except Exception as e:
                prd_discount = None
            prd_item['prd_discount'] = prd_discount
            prd_item['prd_link'] = root_link + item.find(class_='chakra-linkbox__overlay css-1hnz6hu')['href']
            try:
                prd_img = item.find(class_='chakra-image css-112nh')['src']
            except:
                prd_img = None
            prd_item['prd_img'] = prd_img
            return prd_item

        # Using multithreading to scrape details of multiple items from
        # multiple web pages and store the scraped data in a DataFrame.
        all_sub_sub_soup = download_all_page_content()
        with ThreadPoolExecutor(8) as executor:
            results = executor.map(scrap_item_details, all_sub_sub_soup)
            df = pd.DataFrame(results)
            self.df = pd.concat([self.df, df])
