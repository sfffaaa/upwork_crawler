from selenium import webdriver
from bs4 import BeautifulSoup
import os
import pprint

PPRINT = pprint.PrettyPrinter(indent=4)

UPWORK_CRAWLER_WEBSITE_FORMAT = 'https://www.upwork.com/o/profiles/browse/api/search?c=web-mobile-software-dev&pt=independent&page={0}'


os.environ['MOZ_HEADLESS'] = '1'
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


def GetEachFreelancerEntry(soup):
    sections = soup.select('#oContractorResults > div > section')
    freelancers = []
    for section in sections:
        freelancer = {}

        divs = soup.findAll('div')
        freelance_rate = [_ for _ in divs if _.has_attr('data-freelancer-rate')]
        freelancer[KEY_HOURLY_RATE] = float(freelance_rate[0]['data-rate'])
        freelance_earning = [_ for _ in divs if _.has_attr('data-combined-earnings')]
        freelancer[KEY_TOTAL_EARNED] = float(freelance_earning[0]['data-combined-earnings'])
        freelancer[KEY_TOTAL_HOURS] = float(freelance_earning[0]['data-total-hours'])
        freelancer[KEY_TOTAL_FIXPRICE_JOBS] = freelance_earning[0]['data-fp-jobs']
        freelancer[KEY_TOTAL_HOURLY_JOBS] = freelance_earning[0]['data-hourly-jobs']
        location = section.findAll('strong', attrs={'data-ng-attr-title': '{{ fullLocationLabel }}'})
        freelancer[KEY_LOCATION] = location[0]['title']
        name_info = section.findAll('a', attrs={'class': 'freelancer-tile-name'})
        freelancer[KEY_FL_NAME] = name_info[0].text.strip()
        freelancer[KEY_FL_LINK] = 'https://www.upwork.com/' + name_info[0]['href']
        title_info = section.findAll('h4', attrs={'class': 'freelancer-tile-title'})
        freelancer[KEY_FL_TITLE] = title_info[0].text.strip()
        # Note: skills is lacked, we only get 4 in the table view
        skills = section.findAll('a', attrs={'data-log-label': 'tile_skill'})
        freelancer[KEY_SHORT_SKILLS] = [_.text.strip() for _ in skills]
        freelancers.append(freelancer)

    return freelancers


if __name__ == '__main__':
    freelancers = []

    driver = webdriver.Firefox()
    page_number = 1
    # while True:
    if 1:
        driver.get('https://www.upwork.com/o/profiles/browse/api/search?c=web-mobile-software-dev&pt=independent&page={0}'.format(page_number))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        freelancers.extend(GetEachFreelancerEntry(soup))
        if not IsNextPageExist(soup):
            print 'haha'
            # break
        page_number += 1
    # print driver.page_source.encode('utf-8')

    driver.quit()
    PPRINT.pprint(freelancers)
