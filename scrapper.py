from bs4 import BeautifulSoup
import requests
import xml.etree.cElementTree as ET
import cyrtranslit

url_danas = 'https://www.danas.rs/svet/vasington-priznao-crnogorski-jezik/'

kurir = "https://www.kurir.rs/planeta/1544807/nov-biser-ruze-tomasic-predsednik-srbije-unistava-hrvatski-jezik/"
alo_url = "https://www.alo.rs/vesti/region/koliko-slova-ima-crnogorska-azbuka-odgovor-glasi-zavisi-gde-studirate/199085/vest"

portali = {'blic': '02',
           'kurir': '03',
           'danas': '04',
           'alo': '05',
           'novosti': '06',
            'b92': '07',
            'srbijadanas': '08'}

file = open('/Users/lenka/Desktop/spisak.txt', encoding='utf-8')
pretraga = file.read().split('\n')


def pack_xml(article, id):
    portal = article['url'].split('.')[1]

    article_code = 'sr-'+portali[portal]+'-'+str(id)

    root = ET.Element("document")
    root.set('global_id', article_code)


    ET.SubElement(root, "url").text = article['url']
    ET.SubElement(root, "source-id").text = portali[portal]
    ET.SubElement(root, "local-id").text = str(id)
    ET.SubElement(root, "source-name").text = portal
    #ET.SubElement(root, "article")

    article_el = ET.SubElement(root, "article")
    ET.SubElement(article_el, "article-title").text = article['title']
    ET.SubElement(article_el, "article-time").text = article['date']
    ET.SubElement(article_el, "article-author").text = article['author']
    ET.SubElement(article_el, "article-text").text = article['text']
    ET.SubElement(article_el, "article-text-transliterated").text = cyrtranslit.to_latin(article['text'])

    comments = ET.SubElement(root, "comments")
    ET.SubElement(comments, "comment-count").text = str(len(article['comments']))
    comment_list = ET.SubElement(article_el, "comment-list")

    i = 0
    for comment in article['comments']:
        comment_el = ET.SubElement(comment_list, "comments")
        comment_el.set('comment-id', str(i))

        ET.SubElement(comment_el, "comment-parent-id").text = 'XYZ'
        ET.SubElement(comment_el, "comment").text = comment
        ET.SubElement(comment_el, "comment-transliterated").text = cyrtranslit.to_latin(comment)

        i+=1

    tree = ET.ElementTree(root)
    file = article_code+".xml"
    print(article_code)
    tree.write('/Users/lenka/Desktop/'+file, encoding='utf-8')



def extract_kurir(url):
    article = {'url': url}
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article['lead'] = content.find_all('div', attrs={"class": "lead"})[0].text.strip()


    article_div = content.find_all('div', attrs={"itemprop": "articleBody"})


    raw_text = article_div[0].text
    text = ''

    for line in raw_text.split('\n'):
        if not '//' in line and not 'Post by' in line and not 'Autor: Kurir' in line:
            if line != 'Kurir':
                text+=line.replace(', Foto Facebook','').replace('\xa0','')+' '

    article['text'] = text

    #script type = "application/ld+json"

    article['author'] = content.find_all('span', attrs= {'itemprop':"name"})[0].text

    scripts = content.find_all('script', attrs = {"type":"application/ld+json"})

    for el in scripts:
        if 'headline' in el.text:
            for row in el.text.split('\n'):
                if 'headline' in row:
                    article['title'] = row.split(':')[1].replace('"','')
                if 'datePublished' in row:
                    article['date'] = row.split(':')[1].split('T')[0].replace('"','')

    url_comments = url +'/komentari'

    response = requests.get(url_comments, timeout=5)
    content_comments = BeautifulSoup(response.content, "html.parser")

    comments = content_comments.find_all('div', attrs={"class": "com_comment"})

    # class="com_comment (+comReply) “

    article['comments'] = []
    for c in comments:
        comment_text = c.text.split('\n')[4]
        if comment_text.startswith('@'):
            comment_text = c.text.split('\n')[5]

        article['comments'].append(comment_text)

    for el in article:
        print(el, article[el])

    return article

def scrapper_kurir():
    # https://www.kurir.rs/pretraga/strana/3?q=jezika

    i = 0
    for word in pretraga:
        pg = 0
        while pg < 5:
            main_url = 'https://www.kurir.rs/pretraga/strana/'+str(pg)+'?q='+word

            print('main url ', main_url)

            # url_pretraga = main_url+word
            response = requests.get(main_url, timeout=5)
            content = BeautifulSoup(response.content, "html.parser")
            article_links = content.find_all('a', attrs={"class": "itemLnk"})

            for link in article_links:
                print(link.get('href'))

                article = extract_kurir('https://www.kurir.rs' + link.get('href'))
                print('extracted ' + article['url'])
                pack_xml(article, i)
                print('packed xml ' + str(i) + '\n')
                i += 1

            pg += 1

scrapper_kurir()



def extract_alo(url):
    article = {'url':url}

    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")

    text = ''
    article_div = content.find_all('div', attrs={"id":"newsContent"})[0]
    ps = article_div.find_all('p')
    for p in ps:
        if p.a==None and p.text!='PROČITAJTE JOŠ:':
            text += p.text+' '

    article['text'] = text

    article['title'] = content.title.text.split('-')[0] # vise povlaka u naslovu??

    article['author'] = content.find_all('span', attrs={"class":"article-author"})[0].text

    info_div = content.find_all('div', attrs={'class':"mtb10 article-info"})[0].text
    #print(info_div)

    date = info_div.split('\n')[4].strip().split(' ')[0]

    d = date.split('.')[0]
    m = date.split('.')[1]
    y = date.split('.')[2]

    article['date'] = y+'-'+m+'-'+d

    article['comments'] = []
    comments = content.find_all("li", attrs= {"id":"main-comment"})

    for com in comments:
        print(com.find_all('div', attrs={'class':'twelvecol'})[0].text.split('\n')[3])
        article['comments'].append(com.find_all('div', attrs={'class':'twelvecol'})[0].text.split('\n')[3])

    for el in article:
        print(el, article[el])

    return article

def scrapper_alo():
    main_url_alo = 'https://www.alo.rs/article/search?q='
    i = 0
    for word in pretraga:
        url_pretraga = main_url_alo+word
        response = requests.get(url_pretraga, timeout=5)
        content = BeautifulSoup(response.content, "html.parser")
        article_links = content.find_all('a')
        print('len ',len(article_links))

        for link in article_links:
            #print(word, link.text)

            #if i>20:
            #    break
            for keyword in pretraga:
                if keyword in link.text.lower():
                    #print(type(link))
                    #print(link.get('href'))
                    article = extract_alo('https://www.alo.rs'+link.get('href'))
                    print('extracted '+article['url'])
                    pack_xml(article, i)
                    print('packed xml ' +str(i)+'\n')
                    i+=1



def extract_danas(url):
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article_div = content.find_all('div', attrs={"class": "post-content content"})

    article = {'url': url}

    for el in article_div:
        article_span = el.find_all('p')
        text = ''
        for span in article_span:
            text+=' '+span.text

    article['text'] = text

    comments = content.find_all('div', attrs={"class": "comment-content"})

    article['comments'] = []
    for c in comments:
        comment_span = c.find_all('p')
        for span in comment_span:
            article['comments'].append(span.text)

    scripts = content.find_all('script', attrs = {"type":"text/javascript"})

    for el in scripts:
        if 'title' in el.text:
            for row in el.text.split('\n'):
                if 'authors:' in row:
                    article['author'] = row.split(':')[1]
                if 'title:' in row:
                    article['title'] = row.split(':')[1]
                if 'pubdate:' in row:
                    article['date'] = row.split(':')[1].split('T')[0].replace('"','')
                if 'tags:' in row:
                    article['tags'] = row.split(':')[1]

    return article

def scrapper_danas():
    main_url_danas = "https://www.danas.rs/?s="

    for word in pretraga:
        url_pretraga = main_url_danas+word
        response = requests.get(url_pretraga, timeout=5)
        content = BeautifulSoup(response.content, "html.parser")
        article_links = content.find_all('a')
        i = 0
        for link in article_links:
            if i>20:
                break
            if word in link.text.lower():
                print(type(link))
                article = extract_danas(link.get('href'))
                print('extracted '+article['url'])
                pack_xml(article, i)
                print('packed xml ' +str(i)+'\n')
                i+=1




def extract_srbijadanas(url):
    print(url)
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    article_div = content.find_all('div', attrs={"class": "article__body clearfix"})

    article = {'url': url, 'date':''}

    for el in article_div:
        article_span = el.find_all('p')
        text = ''
        for span in article_span:
            text += ' ' + span.text

    article['text'] = text

    comments = content.find_all('div', attrs={"class": "article-comment__comment clearfix"})

    article['comments'] = []
    #print('comments ', len(comments))
    for c in comments:
        #print(c.text)
        comment_span = c.find_all('p')
        for span in comment_span:
            article['comments'].append(span.text)

    article['title'] = content.title.text.split('|')[0]

    article['author'] =  content.find('span', attrs={"class":"article__author"}).text



    for elem in url.split('-')[len(url.split('-'))-3:]:
        article['date']+=elem+'-'

    article['date'] = article['date'].strip('-')
    # div class="article-comment__comment clearfix”

    for el in article:
        print(el, article[el])

    return article

def scrapper_srbijadanas():

    i = 0
    for word in pretraga:
        pg = 0
        while pg<5:
            main_url = 'https://www.srbijadanas.com/search-results/' + word + '?page=' + str(pg)
            print('main url ',main_url)
            response = requests.get(main_url, timeout=5)
            content = BeautifulSoup(response.content, "html.parser")
            article_links = content.find_all('a', attrs={"class":"o-media__link"})

            for link in article_links:
                print(link.get('href'))

                if str.isnumeric(link.get('href').split('-')[len(link.get('href').split('-'))-1]):
                    article = extract_srbijadanas('https://www.srbijadanas.com'+link.get('href'))
                    print('extracted '+article['url'])
                    pack_xml(article, i)
                    print('packed xml ' +str(i)+'\n')
                    i+=1

            pg+=1