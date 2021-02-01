from time import sleep
import csv
import os
import logging

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

FORMAT = "%(asctime)s - %(name)s - %(message)s"
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseSpider:

    def __init__(self, topic):
        self.topic = topic
        self.link = None
        self.source = None

        self.headline_classname = None
        self.date_classname = None
        self.body_classname = None
        self.headline_xpath = None
        self.date_xpath = None
        self.body_xpath = None
        self.next_xpath = None
        self.next_classname = None

        self.max_loop = None

        driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver = driver

    def get_results(self):
        output = []
        elems = []
        for attr in ['date','headline', 'body']:
            attr_classname = attr + "_classname"
            attr_xpath = attr + "_xpath"

            if getattr(self, attr_classname):
                elem = self.driver.find_elements_by_class_name(
                    getattr(self, attr_classname))
                logger.info("elem by classname is :\n%s", [i.text for i in elem])

                if len(elem)==0:
                    try:
                        logger.info("no value, wait 5 seconds")
                        sleep(5)
                        elem = self.driver.find_elements_by_class_name(
                            getattr(self, attr_classname))
                    except:
                        elem = None
                elems.append(elem)

            elif getattr(self, attr_xpath):
                elems.append(self.driver.find_elements_by_xpath(
                getattr(self, attr_xpath)))
                elem = self.driver.find_elements_by_xpath(
                    getattr(self, attr_xpath))
                logger.info("%s elem by xpath is :\n%s", attr, [i.text for i in elem])
                if len(elem)==0:
                    try:
                        logging.info("no value, wait 5 seconds")
                        sleep(5)
                        elem = self.driver.find_elements_by_class_name(
                            getattr(self, attr_classname))
                    except:
                        elem = None
        if all(elems):
            for (date, headline, body) in zip(elems[0], elems[1], elems[2]):
                try:
                    output.append([date.text, headline.text, body.text])
                    logger.info(f"headline is {headline.text}")
                except Exception as e:
                    logger.error(str(e))
                    continue
        else:
            output = False
        return output

    def get_next(self):
        if self.next_xpath:
            next_botton = self.driver.find_elements_by_xpath(self.next_xpath)
        elif self.next_classname:
            next_botton = self.driver.find_elements_by_class_name(self.next_classname)
        try:
            if len(next_botton) == 0:
                return False
            else:
                ActionChains(self.driver).move_to_element(next_botton[0]).click(next_botton[0]).perform()
                return True
        except selenium.common.exceptions.ElementClickInterceptedException:
            sleep(5)
            ActionChains(self.driver).move_to_element(next_botton[0]).click(next_botton[0]).perform()
            return True
        except Exception as e :
            logger.error(str(e))
            return False

    def write_file(self, max_page):
        headers = ['date', 'headline', 'body']
        if not os.path.exists('files'):
            os.mkdir('files')
        with open(f"files/{self.topic}_{self.source}_results.csv", "w+", newline="") as f:
            writer = csv.writer(f)
            writer.writerows([headers, ])

            loop = 0
            if max_page:
                stop = max_page
            else:
                stop = self.max_loop
            while loop < stop:
                logger.info(f"reading from page {loop+1}")
                sleep(5)
                output = self.get_results()
                if output:
                    writer.writerows(output)
                    sleep(5)
                    next_result = self.get_next()
                    logger.info(f"next result is {next_result}")
                    if next_result:
                        loop += 1
                    else:
                        loop = stop
                else:
                    loop = stop

        self.driver.close()


class Cnn(BaseSpider):
    def __init__(self, topic):
        super().__init__(topic)
        self.link = f"https://www.cnn.com/search?size=30&q={self.topic}"
        logger.info(self.link)
        self.source = "CNN"

        self.headline_classname = "cnn-search__result-headline"
        self.date_classname = "cnn-search__result-publish-date"
        self.body_classname = "cnn-search__result-body"
        self.next_xpath = "/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[5]/div/div[3]"
        self.driver.get(self.link)
        results_elem = self.driver.find_elements_by_class_name(
            'cnn-search__results-count')
        logger.info(results_elem[0].text)
        self.max_loop = (int(results_elem[0].text.split(
            "out of ")[1].split(" for")[0]) // 30)+1

class Wsj(BaseSpider):
    def __init__(self, topic):
        super().__init__(topic)
        self.link = f"https://www.wsj.com/search?&query={topic}"
        logger.info(self.link)
        self.source = "WSJ"


        self.headline_xpath = '//*[contains(@class,"WSJTheme--headline")]'
        self.date_xpath = '//*[contains(@class,"WSJTheme--timestamp")]'
        self.body_xpath = '//*[contains(@class,"WSJTheme--summary")]'
        self.next_xpath = '//*[contains(@class,"WSJTheme--next")]'
        self.driver.get(self.link)
        results_elem = self.driver.find_elements_by_class_name(
            'results-count')
        if len(results_elem) != 0:
            logger.info(results_elem[0].text)
            self.max_loop = int(results_elem[0].text.split(" of ")[1])//20+1
        else:
            self.max_loop = 0

if __name__ == "__main__":
    topic="coronavirus"
    # scrape data from web
    cnn_scraper = Cnn(topic)
    cnn_scraper.write_file(2)

    wsj_scraper = Wsj(topic)
    wsj_scraper.write_file(2)
