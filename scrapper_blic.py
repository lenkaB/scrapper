from bs4 import BeautifulSoup
import requests
from scrapper import pretraga,pack_xml

year_counter = {'2015':0, '2016':0, '2017':0, '2018':0,'2019':100, '2020':100}
links = []
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

#driver = webdriver.Chrome(ChromeDriverManager().install())

def scrapper_blic():
    main = 'https://www.blic.rs/search?q='

    i = 204

    for word in pretraga:
        if word=='jezik':
            continue
        pg = 5
        while pg<42:
            main_url = main + word + '&strana=' + str(pg)
            print('main url ', main_url)

            response = requests.get(main_url, timeout=5)
            content = BeautifulSoup(response.content, "html.parser")


            article_links = content.find_all('a')

            for link in article_links:
                link_href = link.get('href')

                if len(link_href)<50 or not 'www.blic' in link_href or 'uslovi' in link_href: #avoid articles from other portals +blic žena
                    continue

                if link_href in links:
                    print('copy link')
                    continue
                links.append(link_href)

                print(link_href)

                article = extract_blic(link_href)
                if not article:
                    continue
                print('extracted ' + article['url'])
                pack_xml(article, i)
                print('packed xml ' + str(i) + '\n')

                i += 1

            jump = 1

            #for y in year_counter:
            #    if year_counter[y]>50:
            #        year_counter.pop(y)
            #        jump=10
            #        break


            pg+=jump

            print('current year counter ', year_counter)
            print('page ', pg)




def extract_blic(url):
    article = {'url':url}
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article['title'] = content.find('h1').text.strip().replace('"','')
    print(article['title'], url)

    article['date'] = content.find("time").get('datetime').split(' ')[0]

    if str.isalpha(article['date']):
        return
        '''
        article['date'] = ''
        for el in content.find("time").get('datetime').split(' ')[1:-1]:
            if str.isalpha(el):
                el+='.'
            article['date']+=el
        '''

    #print(article['date'], content.find("time").get('datetime'))

    year = article['date'].split('.')[2]

    if year not in year_counter or year_counter[year]>100:
        print('wrong year', year)
        return

    if '.' in article['date']:
        y = article['date'].split('.')[2]
        m = article['date'].split('.')[1]
        d = article['date'].split('.')[0]
        article['date'] = y + '-' + m + '-' + d

    #print('year ', year)

    text = ''
    div = content.find('div', attrs={'class':'article-body'})
    for p in div.find_all('p'):
        text+=p.text
    article['text'] = text # plus desc

    keyword_present = False
    for word in pretraga:
        if word in article['text'].lower():
            keyword_present = True
            break

    if not keyword_present:
        print('no keyword')
        return  #

    year_counter[year] += 1

    if not content.find("li",attrs={'class':'author'}):
        return

    article['author'] = content.find("li",attrs={'class':'author'}).text.strip()

    article['comments'] = {}

    '''
    url_comments = url+'#vuukle-comments'
    response_c = requests.get(url_comments, timeout=5)
    comment_page = BeautifulSoup(response_c.content, "html.parser")


    driver.get(url_comments)

    print(url_comments)
    comments = {}

    comment_divs = comment_page.find_all('div', attrs={"class":"v-comment__content"})
    #comment_divs = driver.find_elements_by_class_name('v-comment__content')

    comment_id = 1
    print(len(comment_divs))
    for div in comment_divs:
        print('div')
        comments[str(comment_id)] = div.find('span').text
        comment_id+=1

    article['comments'] = comments
    '''

    for el in article:
        print(el, article[el])

    return article






scrapper_blic()