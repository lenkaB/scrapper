from bs4 import BeautifulSoup
import requests
from scrapper import pretraga, pack_xml

year_counter = {'2015':0, '2016':0, '2017':0, '2018':0,'2019':0, '2020':0}

article_titles = []

url_danas = 'https://www.danas.rs/svet/vasington-priznao-crnogorski-jezik/'


def extract_danas(url):
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article_div = content.find_all('div', attrs={"class": "post-content content"})

    article = {'url': url}

    scripts = content.find_all('script', attrs={"type": "text/javascript"})

    # ADD TO YEARCOUNT + CHECK YEARCOUNT / BREAK
    # CHECK IF ONE OF KEYWORDS IN THE TITLE -> THEN TEXT CHECKING IS UNNECESSARY
    for el in scripts:
        if 'title' in el.text:
            for row in el.text.split('\n'):
                if 'authors:' in row:
                    article['author'] = row.split(':')[1]
                if 'title:' in row:
                    article['title'] = row.split(':')[1]
                    if article['title'] in article_titles:
                        print('copy: ',article['title'])
                        return
                    article_titles.append(article['title'])
                if 'pubdate:' in row:
                    article['date'] = row.split(':')[1].split('T')[0].replace('"', '')

                    year = article['date'].split('-')[0].strip()

                    if year not in year_counter or year_counter[year]>100:
                        print('not the right year ',year)
                        return


    # Extract text and check whether word is present in it
    text = ''
    lead_text = ''
    lead = content.find('div', attrs={'class':'post-intro-content content'})

    if lead:
        lead_text = lead.find('p').text

    for el in article_div:
        article_span = el.find_all('p')
        for span in article_span:
            #print(span.text)
            if 'povezani' in span.text.lower():
                break
            text += ' ' + span.text

    article['text'] = lead_text + text
    print(text)

    keyword_present = False
    for word in pretraga:
        if word in article['text'].lower():
            keyword_present = True
            break

    if not keyword_present:
        print('no keyword')
        return #

    year_counter[year] += 1

    comments = content.find_all('div', attrs={"class": "comment-content"})
    article['comments'] = {}
    com_id = 1
    for c in comments:
        comment_span = c.find_all('p')
        for span in comment_span:
            article['comments'][str(com_id)] = span.text
            com_id+=1


    for el in article:
        print(el, article[el])
    return article


def scrapper_danas():
    i = 1
    for word in pretraga:
        print(word)
        pg_num = 1
        while pg_num<50:
            main_url_danas = "https://www.danas.rs/page/"+str(pg_num)+"/?s="
            url_pretraga = main_url_danas + word
            response = requests.get(url_pretraga, timeout=5)
            print(url_pretraga)
            content = BeautifulSoup(response.content, "html.parser")
            h2s = content.find_all('h2', attrs={"class": "article-post-title"})

            for link in h2s:
                    link = link.find_all('a')[0]
                    print(link.get('href'), link.text)
                    article = extract_danas(link.get('href'))

                    if not article:
                        continue

                    print('extracted ' + article['url'])
                    pack_xml(article, i)
                    print('packed xml ' + str(i) + '\n')
                    i += 1

            pg_num+=1

            print(year_counter)


scrapper_danas()
print(year_counter)