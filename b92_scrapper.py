from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from scrapper import portali, pack_xml, pretraga
import time

url_b92 = 'https://www.b92.net/info/vesti/index.php?yyyy=2019&mm=11&dd=30&nav_category=12&nav_id=1624627'
url_b92_kom = 'https://www.b92.net/info/komentari.php?nav_id=1624627'

year_counter = {'2015':0, '2016':0, '2017':0, '2018':0,'2019':0, '2020':0}
article_titles = []

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.b92.net/search/')


def load_link_from_page_b92(link, id):
        #print(link.get_attribute('href'), link.text)
        article = extract_b92(link.get_attribute('href'))
        if not article or not 'title' in article:
            return -1
        print('extracted ' + article['url'])
        print(article)
        pack_xml(article, id)
        print('packed xml ' + str(id) + '\n')
        #id += 1




def load_links_from_page_b92(current_article_id):
    print('CURRENNT ARTICLE ID ', current_article_id)
    time.sleep(5)
    article_links = driver.find_elements_by_tag_name('a')

    for link in article_links:
        if not link:
            continue

        #if link.text:
        #    print(link.text)

        if link.text and len(link.text.split(' ')) > 2 and not 'Google' in link.text and not 'video' in link.get_attribute('href'):
            test = load_link_from_page_b92(link, current_article_id)
            if test!=-1:
                current_article_id+=1

    return current_article_id

def extract_b92(url):
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article_div = content.find_all('article', attrs={"id": "article-content"})

    article = {'url': url, 'description':''}

    scripts = content.find_all('script', attrs={"type": "application/ld+json"})
    for el in scripts:
        if 'headline' in el.text:
            for row in el.text.split('\n'):
                if 'headline' in row:

                    if len(row.split(':'))>2:
                        title = ''
                        for el in row.split(':')[1:]:
                            title+=': '+el
                        article['title'] = title
                    else:
                        article['title'] = row.split(':')[1]



                    if article['title'] in article_titles:
                        print('copy ', article['title'])
                        return
                    article_titles.append(article['title'].replace('&quot;','')) #TODO
                if 'datePublished' in row:
                    article['date'] = row.split(':')[1].split('T')[0].strip().replace('"','') #fix
                    year = article['date'].split('-')[0]
                    if year not in year_counter: # or year_counter[year]>50:
                        print('bad year ',year)
                        return

                    # year counter

                if 'description' in row:
                    article['description'] = row.split(':')[1]

    text = ''

    for el in article_div:
        #print(el)
        article_span = el.find_all('p')

        for span in article_span:
            if '\n' not in span.text and 'Pročitajte još:' not in span.text and 'FOTO' not in span.text:
                try:
                    text+=' '+span.text
                except:
                    continue

    article['text'] = article['description']+ text

    keyword_present = False

    for word in pretraga:
        if 'title' not in article:
            return
        if word in article['title'].lower():
            keyword_present = True
            break
    if not keyword_present:
        for word in pretraga:
            if word in article['text'].lower():
                keyword_present = True
                break

    if not keyword_present:
        print('no keyword')
        return  #

    year_counter[year] += 1

    url_comments = 'https://www.b92.net/info/komentari.php?'+url.split('&')[len(url.split('&'))-1]
    response = requests.get(url_comments, timeout=5)
    content_comments = BeautifulSoup(response.content, "html.parser")

    comments = content_comments.find_all('div', attrs={"class": "comments"})

    article['comments'] = {}
    comment_id = 1 #  replies start with @
    for c in comments:
        #print(c,c.text)
        comment_span = c.find_all('li')
        for span in comment_span:
            if len(span.text.split('\n'))>1:
                comment = span.text.split('\n')[1]+span.text.split('\n')[2]
                article['comments'][str(comment_id)] = comment.replace('\t','').replace('@','').replace('\r',' ').split('(')[0]
                comment_id+=1


    article['author'] = ''
    if len(content.find_all('small'))>0:
        for s in content.find_all('small')[0].find_all('span'):
            if len(s.text.split(':'))>1:
                article['author'] = s.text.split(':')[1].split('\n')[0]

    title = article['title']
    if '&quot;' in title:
        title = title.replace('&quot;', '')
        # print('clean ', title)
        article['title'] = title

    if title.strip().endswith(','):
        article['title'] = title[:-2]
        title = title[:-2]
        # print('comma')

    if not title.endswith('"'):
        print('incomplete ', title)

    for e in article:
        print(e)
        print(article[e])

    return article


def scrapper_b92(word, current_article_id):
    # search and wait to load
    box = driver.find_element_by_id('gsc-i-id2')
    box.clear()
    box.send_keys(word)
    box.send_keys('\ue007')

    time.sleep(3)
    driver.find_element_by_class_name("gsc-option-selector").click()
    options = driver.find_elements_by_class_name("gsc-option")
    for option in options:
        if option.text == 'Relevantnosti':
            option.click()

    # look for page numbers and change pages
    page_no = 1

    while page_no<11:
        #time.sleep(3)
        current_article_id = load_links_from_page_b92(current_article_id)
        page_numbers = driver.find_elements_by_class_name("gsc-cursor-page")
        for page_number in page_numbers:
            if page_number.text == str(page_no):
                print('switching to page '+str(page_no))
                driver.execute_script("window.scrollTo(0, window.scrollY + 200)")
                page_number.click()
                page_no+=1
                break



        print(year_counter)

    return current_article_id

current_article_id = 167
for word in pretraga:
    if word in ['jezik', 'jezika']:
        continue
    current_article_id = scrapper_b92(word, current_article_id)

#print(year_counter)