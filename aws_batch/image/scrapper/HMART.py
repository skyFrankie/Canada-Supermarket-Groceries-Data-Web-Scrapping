import os
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapper.SCRAPPER import STORESCRAPPER
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException
from dataclasses import dataclass, field
import time
import pytz


@dataclass
class HMARTSCRAPPER(STORESCRAPPER):
    url_list: dict = field(init=False)
    df: pd.DataFrame = field(init=False)
    event_num: int = int(os.environ['EVENT_NUM'])

    def __post_init__(self):
        self.df = pd.DataFrame()
        self.url_list = dict()
        self.store_name = 'HMart'
        self.initialize_web_drive()


    def scrap_main(self):
        self.drive.get(self.params.get('scrapping_websites', None).get(self.store_name, None))
        time.sleep(60)
        self.scroll_to_category()
        #entry to sub cat page
        current_url = self.drive.current_url
        self.get_all_prd_url(current_url)
        self.scroll_all_items()
        self.df.to_csv(self.output_filepath, index=False)

    def scroll_to_category(self):
        current_url = self.drive.current_url
        for re_time in range(15):
            try:
                #wait for the category list show up
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="html-body"]/div[2]/div[2]/header/div[2]/span[1]')
                    )
                ).click()
                if self.event_num == 2 or self.event_num == 3:
                    self.wait.until(
                        EC.element_to_be_clickable(
                            (By.CLASS_NAME, f'ammenu-item.-main.nav-{self.event_num}')
                        )
                    ).click()
                else:
                    self.wait.until(
                        EC.element_to_be_clickable(
                            (By.CLASS_NAME,f'ammenu-item.-main.-parent.nav-{self.event_num}')
                        )
                    ).click()
                break
            except TimeoutException:
                print('Retrying locating the category list...')
                self.drive.get(current_url)
                time.sleep(15)
            except ElementClickInterceptedException:
                print('Retrying locating the category list...')
                self.drive.get(current_url)
                time.sleep(15)
            except WebDriverException:
                self.reinitialize_web_drive(current_url)


    def get_all_prd_url(self, current_url):
        for re_time in range(15):
            try:
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, 'products.list.items.product-items')
                    )
                )
                break
            except TimeoutException:
                print('Retrying locating the category list...')
                self.drive.get(current_url)
                time.sleep(15)
            except WebDriverException:
                self.reinitialize_web_drive(current_url)
        page_list = None
        try:
            page_list = self.drive.find_element(By.XPATH, '//*[@id="maincontent"]/div/div[1]/div[4]/div/div/ul')
        except:
            print('multiple page not found in this category...')
        if page_list:
            tmp_soup = BeautifulSoup(page_list.get_attribute('innerHTML'), "html.parser")
            all_page_num = len(tmp_soup.find_all('li'))
        else:
            all_page_num = 2
        cat = self.drive.find_element(By.CLASS_NAME, 'base').text
        for i in range(1, all_page_num):
            if i != 1:
                current_url += f'?p={i}'
            self.drive.get(current_url)
            page = requests.get(current_url)
            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find_all('li', class_="item product product-item")
            prd_url_list = [(result.find_all('a', href=True)[0]['href'], result.find('img', class_="product-image-photo")['src']) for result in results]
            print(f'Product in this page: {len(prd_url_list)}.')
            if cat not in self.url_list:
                self.url_list[cat] = prd_url_list
            else:
                self.url_list[cat].extend(prd_url_list)

    def scroll_all_items(self):
        def scrap_hmart(url_pack):
            url = url_pack[0]
            prd_img_url = url_pack[1]
            data = dict()
            toronto_tz = pytz.timezone("America/Toronto")
            data['scrap_date'] = datetime.now(toronto_tz).strftime('%Y-%m-%d')
            data['prd_url'] = url
            data['prd_img'] = prd_img_url
            prd_page = requests.get(url)
            prd_soup = BeautifulSoup(prd_page.content, "html.parser")
            prd_prices = prd_soup.find_all('span', class_="price")
            data['prd_discount'] = False
            data['sub_category'] = None
            data['store'] = 'HMart'
            if len(prd_prices) > 1:
                data['prd_discount'] = True
                data['org_price'] = prd_prices[1].text
                data['prd_price'] = prd_prices[0].text
            else:
                data['org_price'] = prd_prices[0].text
                data['prd_price'] = prd_prices[0].text
            data['on_sale_cat'] = 'SAVING' if data['prd_discount'] else None
            prd_findings = prd_soup.find_all('th')
            for j, x in enumerate(['prd_brand', 'prd_name', 'average_unit', 'prd_id_in_store']):
                data[x] = prd_findings[j].parent.select('td')[0].get_text()
            return data
        for key, url_val in self.url_list.items():
            with ThreadPoolExecutor(8) as executor:
                results = executor.map(scrap_hmart, url_val)
                df = pd.DataFrame(results)
                df['category'] = key
                self.df = pd.concat([self.df, df])
