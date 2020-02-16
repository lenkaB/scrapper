from bs4 import BeautifulSoup
import requests
from scrapper import pretraga, pack_xml


kurir_komentari = 'https://www.kurir.rs/crna-hronika/3407595/platio-2-500-evra-za-noc-sa-radom-manojlovic-i-jos-1000-za-ruze-bisnimen-u-velikoj-seks-parevari-citajte-u-kuriru'
kurir = "https://www.kurir.rs/planeta/1544807/nov-biser-ruze-tomasic-predsednik-srbije-unistava-hrvatski-jezik/"

year_counter = {'2015':0, '2016':0, '2017':0, '2018':0} #'2019':0, '2020':0}
links = []

# WHEN YEARCOUNTER REACHES MAX GO TO FURTHER PAGE (articles from 2015/16)

def extract_kurir(url):
    article = {'url': url}
    print(url)
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article['lead'] = content.find_all('div', attrs={"class": "lead"})[0].text.strip()

    article_div = content.find_all('div', attrs={"itemprop": "articleBody"})

    scripts = content.find_all('script', attrs={"type": "application/ld+json"})
    for el in scripts:
        if 'headline' in el.text:
            for row in el.text.split('\n'):
                if 'headline' in row:
                    article['title'] = row.split(':')[1].replace('"', '')
                if 'datePublished' in row:
                    article['date'] = row.split(':')[1].split('T')[0].replace('"', '')

                    year = article['date'].split('-')[0].strip()

                    if year not in year_counter or year_counter[year] > 100:
                        print('not the right year ', year)
                        return


    raw_text = article_div[0].text
    text = ''

    for line in raw_text.split('\n'):
        if not '//' in line and not 'Post by' in line and not 'Autor: Kurir' in line and not line.startswith('foto') and line!='Kurir':
            if line == 'SUTRA U KURIRU SAZNAJTE JOŠ' or 'NE PROPUSTITE' in line:
                break
            text+=line.replace(', Foto Facebook','').replace('\xa0','')+' '

    article['text'] = article['lead']+'. '+text

    keyword_present = False
    for word in pretraga:
        if word in article['text'].lower():
            keyword_present = True
            break

    if not keyword_present:
        print('no keyword')
        return  #

    year_counter[year]+=1
    article['author'] = content.find_all('span', attrs= {'itemprop':"name"})[0].text


    url_comments = url +'/komentari'

    response = requests.get(url_comments, timeout=5)
    content_comments = BeautifulSoup(response.content, "html.parser")

    comments = content_comments.find_all('div', attrs={"class": "com_comment"})

    article['comments'] = {}
    com = 1
    com_reply = 1
    for c in comments:
        comment_text = c.text.split('\n')[4]

        if comment_text.startswith('@'):
            #print(comment_text) # REPLY
            comment_text = c.text.split('\n')[5]
            comment_id = str(com-1)+'-'+str(com_reply)
            com_reply+=1

        else:
            comment_id = str(com)
            com+=1
            com_reply = 1

        article['comments'][comment_id] = comment_text

    for el in article:
        print(el, article[el])

    return article


def scrapper_kurir():
    i = 523
    for word in pretraga:
        if word in ['jezik', 'jezika']:
            continue
        pg = 1
        while pg < 15:
            main_url = 'https://www.kurir.rs/pretraga/strana/'+str(pg)+'?q='+word
            print('main url ', main_url)

            response = requests.get(main_url, timeout=5)
            content = BeautifulSoup(response.content, "html.parser")
            article_links = content.find_all('a', attrs={"class": "itemLnk"})

            for link in article_links:
                if type(link)==str:
                    continue
                link_href = link.get('href')

                if link_href in links:
                    print('copy link')
                    continue
                links.append(link_href)

                if link_href.split('/')[len(link_href.split('/'))-1].startswith('video'):
                    print('video link ',link_href)
                    continue

                article = extract_kurir('https://www.kurir.rs' + link_href)
                if not article:
                    continue
                print('extracted ' + article['url'])
                pack_xml(article, i)
                print('packed xml ' + str(i) + '\n')
                i += 1

            pg += 1
            print('current year counter ',year_counter)
            print('page ', pg)

#scrapper_kurir()
print(year_counter)