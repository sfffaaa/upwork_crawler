from selenium import webdriver
from bs4 import BeautifulSoup
import os
import pprint
import json
import time
import random
import logging
PPRINT = pprint.PrettyPrinter(indent=4)


MAX_CRAWLER_PAGES = 601
CRAWLER_SLEEP_TIME = 30
UPWORK_MAIN_WEBSITE = 'https://www.upwork.com'
UPWORK_CRAWLER_WEBSITE_FORMAT = UPWORK_MAIN_WEBSITE + '/o/profiles/browse/api/search?c=web-mobile-software-dev&pt=independent&page={0}'

RESULT_DIR_PATH = 'result'
RESULT_FILE_PREFIX = 'data.json'


# ----- Internal use so user shouldn't change below parameter -----
os.environ['MOZ_HEADLESS'] = '1'
CAPTUA_WAIT_TIME = 60
CAPTUA_RETRY_TIME = 5
KEY_FL_NAME = 'name'
KEY_FL_LINK = 'link'
KEY_FL_TITLE = 'title'
KEY_HOURLY_RATE = 'hourly_rate'
KEY_TOTAL_EARNED = 'total_earned'
KEY_TOTAL_HOURS = 'total_hours'
KEY_TOTAL_FIXPRICE_JOBS = 'total_fixprice_jobs'
KEY_TOTAL_HOURLY_JOBS = 'total_hourly_jobs'
KEY_LOCATION = 'location'
KEY_SHORT_SKILLS = 'skills'


def IsNextPageExist(soup):
    next_page = soup.select('#oContractorResults > div > footer > section > div > ul > li.pagination-next')
    if 1 != len(next_page):
        return False
    elif not next_page[0].has_attr('class'):
        return True
    elif 'disabled' in next_page[0]['class']:
        return False
    return True


class Freelancer():
    def __init__(self, section):
        freelancer = {}
        divs = section.findAll('div')
        freelance_rate = [_ for _ in divs if _.has_attr('data-freelancer-rate')]
        freelancer[KEY_HOURLY_RATE] = float(freelance_rate[0]['data-rate'])
        freelance_earning = [_ for _ in divs if _.has_attr('data-combined-earnings')]
        if len(freelance_earning):
            freelancer[KEY_TOTAL_EARNED] = float(freelance_earning[0]['data-combined-earnings'])
            freelancer[KEY_TOTAL_HOURS] = float(freelance_earning[0]['data-total-hours'])
            freelancer[KEY_TOTAL_FIXPRICE_JOBS] = freelance_earning[0]['data-fp-jobs']
            freelancer[KEY_TOTAL_HOURLY_JOBS] = freelance_earning[0]['data-hourly-jobs']
        else:
            freelancer[KEY_TOTAL_EARNED] = 0
            freelancer[KEY_TOTAL_HOURS] = 0
            freelancer[KEY_TOTAL_FIXPRICE_JOBS] = 0
            freelancer[KEY_TOTAL_HOURLY_JOBS] = 0

        location = section.findAll('strong', attrs={'data-ng-attr-title': '{{ fullLocationLabel }}'})
        freelancer[KEY_LOCATION] = location[0]['title']
        name_info = section.findAll('a', attrs={'class': 'freelancer-tile-name'})
        freelancer[KEY_FL_NAME] = name_info[0].text.strip()
        freelancer[KEY_FL_LINK] = UPWORK_MAIN_WEBSITE + name_info[0]['href']
        title_info = section.findAll('h4', attrs={'class': 'freelancer-tile-title'})
        freelancer[KEY_FL_TITLE] = title_info[0].text.strip()
        # Note: skills is lacked, we only get 4 in the table view
        skills = section.findAll('a', attrs={'data-log-label': 'tile_skill'})
        freelancer[KEY_SHORT_SKILLS] = [_.text.strip() for _ in skills]
        for k, v in freelancer.items():
            setattr(self, k, v)

    def __str__(self):
        return json.dumps(vars(self))

    def __repr__(self):
        return '<Freelancer {0}>'.format(self.__str__())


class MyJsonCoventor(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Freelancer):
            return obj.__str__()
        else:
            return json.JSONEncoder.default(self, obj)


def ServerAskCapcha(soup):
    for h2 in soup.findAll('h2'):
        if 'browser supports JavaScript' in h2.text:
            return True
    return False


def SetupLogger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-2s %(message)s',
                        datefmt='%Y%m%d-%H%M%S',
                        filename='my.log')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-2s %(message)s',
                                  datefmt='%Y%m%d-%H%M%S')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)


if __name__ == '__main__':

    SetupLogger()

    freelancers = []

    start_time_str = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
    driver = webdriver.Firefox()
    page_number = 1
    wait_capture_time = 1
    try:
        # if 1:
        while page_number < MAX_CRAWLER_PAGES and wait_capture_time < CAPTUA_RETRY_TIME:
            website_url = UPWORK_CRAWLER_WEBSITE_FORMAT.format(page_number)
            logging.info('Start query {0}'.format(website_url))
            driver.get(UPWORK_CRAWLER_WEBSITE_FORMAT.format(website_url))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            if ServerAskCapcha(soup):
                logging.warning('Enter capcha phase {0}'.format(wait_capture_time))
                time.sleep(CAPTUA_WAIT_TIME * wait_capture_time)
                driver.get(UPWORK_MAIN_WEBSITE)
                wait_capture_time += 1
                continue
            wait_capture_time = 1
            sections = soup.select('#oContractorResults > div > section')
            freelancers.extend([Freelancer(section) for section in sections])
            if not IsNextPageExist(soup):
                logging.info('Reach the end in {0}'.format(website_url))
                break
            page_number += 1
            sleep_time = random.randint(0, CRAWLER_SLEEP_TIME * 100) / 100
            logging.info('Wait {0}s for next query'.format(sleep_time))
            time.sleep(sleep_time)
    except Exception as e:
        logging.error(driver.page_source.encode('utf-8'))
        raise
    finally:
        driver.quit()

    if wait_capture_time == CAPTUA_RETRY_TIME:
        status = 'fail'
        logging.info('Force stop because the website block me')
    elif page_number == MAX_CRAWLER_PAGES:
        status = 'reach_max'
        logging.info('Success finished because page_number {0} reach max crawl page'.format(page_number))
    else:
        status = 'no_next'
        logging.info('Success finished because page_number {0} has no next page'.format(page_number))

    if not os.path.isdir(RESULT_DIR_PATH):
        os.makedirs(RESULT_DIR_PATH)

    filename = '{0}.{1}.{2}'.format(RESULT_FILE_PREFIX, status, start_time_str)
    with open(os.path.join(RESULT_DIR_PATH, filename), 'w') as f:
        json.dump(freelancers, f, cls=MyJsonCoventor)
