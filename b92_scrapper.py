
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from scrapper import portali, pack_xml, pretraga

url_b92 = 'https://www.b92.net/info/vesti/index.php?yyyy=2019&mm=11&dd=30&nav_category=12&nav_id=1624627'
url_b92_kom = 'https://www.b92.net/info/komentari.php?nav_id=1624627'

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(20)
driver.get('https://www.b92.net/search/')


def load_link_from_page_b92(link, id):

        #print(type(link), link.text, link.get_attribute("href"))
        print(link.get_attribute('href'), link.text)
        article = extract_b92(link.get_attribute('href'))
        print('extracted ' + article['url'])
        pack_xml(article, id)
        print('packed xml ' + str(id) + '\n')
        #id += 1


def load_links_from_page_b92(current_article_id):
    print('CURRENNT ARTICLE ID ', current_article_id)
    wait = WebDriverWait(driver, 1000)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gsc-table-result')))

    driver.implicitly_wait(1000)
    article_links = driver.find_elements_by_tag_name('a')


    print(len(article_links))
    for link in article_links:
        print(type(link), link, link.is_enabled(),link.is_selected())

        if link.text:
            print(link.text)

        if link.text and len(link.text.split(' ')) > 2 and not 'Google' in link.text:

            load_link_from_page_b92(link, current_article_id)
            current_article_id+=1


    return current_article_id

def extract_b92(url):
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article_div = content.find_all('article', attrs={"id": "article-content"})

    article = {'url': url}

    text = ''

    for el in article_div:
        #print(el)
        article_span = el.find_all('p')

        for span in article_span:
            if '\n' not in span.text and 'Pročitajte još:' not in span.text and 'FOTO' not in span.text:
                #print(span.text+'\n')
                text+=' '+span.text

    article['text'] = text


    url_comments = 'https://www.b92.net/info/komentari.php?'+url.split('&')[len(url.split('&'))-1]
    response = requests.get(url_comments, timeout=5)
    content_comments = BeautifulSoup(response.content, "html.parser")

    comments = content_comments.find_all('div', attrs={"class": "comments"})

    article['comments'] = []
    for c in comments:
        #print(c,c.text)
        comment_span = c.find_all('li')
        for span in comment_span:
            if len(span.text.split('\n'))>1:
                comment = span.text.split('\n')[1]+span.text.split('\n')[2]
                article['comments'].append(comment.replace('\t','').replace('@','').replace('\r',' '))


    article['author'] = ''
    for s in content.find_all('small')[0].find_all('span'):
        if len(s.text.split(':'))>1:
            article['author'] = s.text.split(':')[1].split('\n')[0]

    scripts = content.find_all('script', attrs = {"type":"application/ld+json"})

    for el in scripts:
        if 'headline' in el.text:
            for row in el.text.split('\n'):
                #if 'author' in row:
                #    article['author'] = row.split(':')[1] #fix
                if 'headline' in row:
                    article['title'] = row.split(':')[1]
                if 'datePublished' in row:
                    article['date'] = row.split(':')[1].split('T')[0] #fix
                if 'description' in row:
                    article['description'] = row.split(':')[1]

    for e in article:
        print(article[e])

    return article


def scrapper_b92():


    # search and wait to load TODO all terms
    box = driver.find_element_by_id('gsc-i-id2')
    box.send_keys('jezik')
    box.send_keys('\ue007')

    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gs-title')))

    waits = {2:'gsc-url-top', 3:'gsc-table-result'}

     #load links from a certain page:
    current_article_id = 1

    while current_article_id<50:

        current_article_id = load_links_from_page_b92(current_article_id)

       # look for page numbers and change pages
        page_numbers = driver.find_elements_by_class_name("gsc-cursor-page")
        page_no = 2
        print('len ',len(page_numbers), page_numbers[0])

        for page_number in page_numbers:
            print(page_number.text)
            if page_number.text == str(page_no):
                print('switching to page '+str(page_no))
                driver.execute_script("window.scrollTo(0, window.scrollY + 200)")
                #page_number.location_once_scrolled_into_view().click()

                page_number.click()


                print('hello')
                wait2 = WebDriverWait(driver, 100000)
                print('hellooooo')
                wait2.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gsc-url-top')))

                print('now I want to load articles from page '+str(page_no))

                current_article_id = load_links_from_page_b92(current_article_id)
                page_no+=1

scrapper_b92()