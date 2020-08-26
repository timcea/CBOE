# crawl CBOE site for daily notional amount on exchanges

from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import pandas as pd
import csv
import time
import logging

start_date = '2015-01-01'
maxtry = 10
date_list = [d.strftime('%Y-%m-%d') for d in pd.date_range(start=start_date, end=datetime.datetime.today()).tolist()]
date_list.reverse()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cboe')
logger.info('Welcome to CBOE crawling')

fw = csv.writer(open('notional.csv', mode='w'))

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

for d in date_list:
    url = 'https://markets.cboe.com/us/equities/market_share/market/' + d
    try:
        driver.get(url)
        btn = driver.find_element_by_id('notionalvalueSummaryBtn')
        # check if Notional Value selected; if not, sleep for 1 sec unles tried maxtry times
        driver.execute_script("arguments[0].click();", btn)
        for i in range(maxtry):
            source = driver.page_source
            soup = BeautifulSoup(source, 'lxml')
            vol = soup.find("tr", class_="total").find_all("td", class_="idx_val")[3].get_text()
            logger.debug(f'{d} iter: {i} v: {vol}')
            if vol[0] == '$':
                vol = int(vol.replace(',','')[1:])
                if vol > 0:
                    logger.info(f'{d} {vol}')
                    fw.writerow([d, vol])
                break
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
        # give it a break...
        time.sleep(1)
    except Exception as e:
        logger.error(f'{d} {vol} {str(e)}')
