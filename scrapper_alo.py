from bs4 import BeautifulSoup
import requests
from scrapper import pretraga, pack_xml
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome(ChromeDriverManager().install())
main_url_alo = 'https://www.alo.rs/article/search?q='


year_counter = {'2015':0, '2016':0, '2017':0, '2018':0,'2019':0}
links = []

def extract_alo(url):
    article = {'url':url}
    print(url)

    response = requests.get(url, timeout=20)
    content = BeautifulSoup(response.content, "html.parser")

    if not article:
        return

    article['title'] = content.title.text.split('-')[0] # vise povlaka u naslovu??

    info_div = content.find_all('div', attrs={'class': "mtb10 article-info"})[0].text
    date = info_div.split('\n')[4].strip().split(' ')[0]

    d = date.split('.')[0]
    m = date.split('.')[1]
    y = date.split('.')[2]

    if y.strip() not in year_counter:# or year_counter[y.strip()] > 50:
        print('not the right year ', y.strip())
        return

    text = ''
    article_div = content.find_all('div', attrs={"id":"newsContent"})[0]
    ps = article_div.find_all('p')
    for p in ps:
        if p.a==None and p.text!='PROČITAJTE JOŠ:':
            text += p.text+' '

    article['text'] = text
    article['author'] = content.find_all('span', attrs={"class":"article-author"})[0].text
    article['lead'] = content.find_all('p', attrs={"class":"lead mtb20"})[0].text
    article['text'] = article['lead']+' '+article['text']


    keyword_present = False
    for word in pretraga:
        if word in article['text'].lower():
            keyword_present = True
            break

    if not keyword_present:
        print('no keyword')
        return  #

    year_counter[y.strip()] += 1
    article['date'] = y+'-'+m+'-'+d

    article['comments'] = {}
    comments = content.find_all("li", attrs= {"id":"main-comment"})

    com_id = 1  # very few comments, rare replies
    for com in comments:
        #print(com.find_all('div', attrs={'class':'twelvecol'})[0].text.split('\n')[3])
        article['comments'][str(com_id)] = com.find_all('div', attrs={'class':'twelvecol'})[0].text.split('\n')[3]
        com_id+=1

    for el in article:
        print(el, article[el])

    return article



def scrapper_alo():
    i = 364
    #while i<1000:

    for word in pretraga:
        if word in ['jezik','jezika','jeziku']:#,'jezikom']:
            continue

        url_pretraga = main_url_alo+word
        print('main url',url_pretraga)
        driver.get(url_pretraga)
        scroll = 0

        while scroll<20:
            time.sleep(5)
            article_links = driver.find_elements_by_tag_name('a')
            print('len ',len(article_links))

            for link in article_links:
                link_href = link.get_attribute('href')
                if link_href in links:
                    #driver.execute_script("window.scrollTo(0, window.scrollY + 20)")
                    continue
                links.append(link_href)
                if link_href and (link_href).endswith('vest'):
                    print(link_href, link.text)
                    article = extract_alo(link_href)
                    if not article:
                        continue
                    print('extracted '+article['url'])
                    pack_xml(article, i)
                    print('packed xml ' +str(i)+'\n')
                    i+=1

            driver.execute_script("window.scrollTo(0, window.scrollY + 300)")
            scroll+=1
            try:
                button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "PRIKAŽI JOŠ REZULTATA")))
                button.click()
                driver.execute_script("window.scrollTo(0, window.scrollY + 300)")

            finally:
                print('cannot locate BUTTON',)

            print(year_counter)


#scrapper_alo()
print(year_counter)