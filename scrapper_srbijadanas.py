from bs4 import BeautifulSoup
import requests
from scrapper import pretraga, pack_xml

year_counter = {'2015':0, '2016':0, '2017':0, '2018':0, '2019':0}

links = []


def extract_srbijadanas(url):
    print('extracting ',url)
    response = requests.get(url, timeout=15)
    content = BeautifulSoup(response.content, "html.parser")
    article_div = content.find_all('div', attrs={"class": "article__body clearfix"})

    article = {'url': url, 'date': ''}

    article['title'] = content.title.text.split('|')[0]

    for elem in url.split('-')[len(url.split('-')) - 3:]:
        article['date'] += elem + '-'

    article['date'] = article['date'].strip('-')

    year = article['date'].split('-')[0].strip() #sometime year is at 0 sometime 2

    if year.isnumeric() and int(year)<2000:
        year = article['date'].split('-')[2].strip()

    if year not in year_counter: # or year_counter[year] > 100:
        print('incorrect year ',year)
        return


    article['description'] = content.find('meta',attrs={'name':'description'}).text

    for el in article_div:
        article_span = el.find_all('p')
        text = ''
        for span in article_span:
            #print(span.text)
            if not 'Foto:' in span.text and (len(span.text)>2 and not str.isupper(span.text[2])):
                text += ' ' + span.text

    article['text'] = article['description'] + text

    keyword_present = False
    for word in pretraga:
        if word in article['text'].lower():
            keyword_present = True
            break

    if not keyword_present:
        print('no keyword')
        return #

    year_counter[year] += 1

    comments = content.find_all('div', attrs={"class": "article-comment__comment clearfix"})

    article['comments'] = {}
    # print('comments ', len(comments))
    comment_id = 1
    for c in comments:
        # print(c.text)
        comment_span = c.find_all('p')
        for span in comment_span:
            article['comments'][str(comment_id)] = span.text.strip()

    article['author'] = content.find('span', attrs={"class": "article__author"}).text


    for el in article:
        print(el, article[el])

    return article


def scrapper_srbijadanas():
    i = 970
    for word in pretraga:
        #if word in ['jezik', 'jezika', 'jeziku']:
        #    continue
        pg = 349
        while pg <400 : # TODO

            main_url = 'https://www.srbijadanas.com/search-results/' + word + '?page=' + str(pg)
            print('main url ', main_url)
            response = requests.get(main_url, timeout=15)
            content = BeautifulSoup(response.content, "html.parser")
            article_links = content.find_all('a', attrs={"class": "o-media__link"})

            for link in article_links:
                link_href = link.get('href')

                if link_href in links or '/zadruga/' in link_href:
                    continue
                links.append(link_href)

                # if the link ends with a number its an article
                if str.isnumeric(link.get('href').split('-')[len(link.get('href').split('-')) - 1]):
                    article = extract_srbijadanas('https://www.srbijadanas.com' + link.get('href'))
                    if not article:
                        continue
                    print('extracted ' + article['url'])
                    pack_xml(article, i)
                    print('packed xml ' + str(i) + '\n')
                    i += 1

            pg += 1
            print(year_counter)


scrapper_srbijadanas()
print(year_counter)