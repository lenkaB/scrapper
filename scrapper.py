from bs4 import BeautifulSoup
import requests
import xml.etree.cElementTree as ET
import cyrtranslit

#url = 'https://www.danas.rs/kultura/srpski-jezik-nije-ugrozen/'

url_danas = 'https://www.danas.rs/svet/vasington-priznao-crnogorski-jezik/'
url_b92 = 'https://www.b92.net/info/vesti/index.php?yyyy=2019&mm=11&dd=30&nav_category=12&nav_id=1624627'
url_b92_kom = 'https://www.b92.net/info/komentari.php?nav_id=1624627'

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


    url_comments = 'https://www.b92.net/info/komentari.php?'+url_b92.split('&')[len(url_b92.split('&'))-1]
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


    scripts = content.find_all('script', attrs = {"type":"application/ld+json"})

    for el in scripts:
        if 'headline' in el.text:
            for row in el.text.split('\n'):
                if 'author' in row:
                    article['author'] = row.split(':')[1] #fix
                if 'headline' in row:
                    article['title'] = row.split(':')[1]
                if 'datePublished' in row:
                    article['date'] = row.split(':')[1].split('T')[0] #fix
                if 'description' in row:
                    article['description'] = row.split(':')[1]

    for e in article:
        print(article[e])

    return article

kurir = "https://www.kurir.rs/planeta/1544807/nov-biser-ruze-tomasic-predsednik-srbije-unistava-hrvatski-jezik/"


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


#alo_url = "https://www.alo.rs/vesti/region/koliko-slova-ima-crnogorska-azbuka-odgovor-glasi-zavisi-gde-studirate/199085/vest"

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
    tree.write('/Users/lenka/Desktop/'+file, encoding='utf-8')

import selenium
from selenium import webdriver

def scrapper_b92():
    driver = webdriver.Chrome()
    driver.get(url_b92)
    id_box = driver.find_element_by_class_name('search')
    id_box.send_keys('jezik')
    id_box.send_keys()  # enter key



'''
Root element bi bio "document" koji bi imao atribut "global-id" - string koji ima istu vrednost kao naziv xml dokumenta (osim ekstenzije), npr. "sr-01-254". Deca čvora "document" su:
    - "url" - string koji sadrži URL članka
    - "source-id" - string koji sadrži ID sajta, u gorenavedenom formatu (ovde i u sledećoj stavci imamo određenu redundantnost u čuvanju informacija, pošto se ista stvar vidi već iz naziva fajla i iz "global-id" atributa, ali mislim da nije loše da beležimo i ovde)
    - "local-id" - integer koji sadrži ID broj članka,  dobijen na gorenavedeni način
    - "source-name" - string koji sadrži ime izvora (npr. "Politika")
    - "article" element koji je dete od "document" i sadrži sledeće čvorove-listove:
        - "article-title" - string koji sadrži naslov članka
        - "article-time" - string koji sadrži datum objavljivanja članka, u formatu YYYY-MM-DD
        - "article-author" - string koji sadrži ime autora članka (ako je navedeno, ako nije onda prazan string)
        - "article-text" - string koji sadrži ceo tekst članka
        - "article-text-transliterated" - string koji sadrži ceo tekst članka preslovljen za latinicu. U praksi će ovo biti bitno tj. različito od "article-text" samo za sajtove na srpskom gde se mogu javiti tekstovi i/ili komentari na ćirilici. Za transliteraciju možeš koristiti neke postojeće biblioteke (npr. https://github.com/opendatakosovo/cyrillic-transliteration)
    - "comments" element koji je dete od "document" i sadrži sledeće čvorove:
        - "comment-count" - integer koji predstavlja broj komentara o posmatranom članku
        - "comment-list" - čvor koji predstavlja roditeljski čvor za sve elemente o pojedinačnim komentarima i koji ima dece-čvorova onoliko koliko je navedeno u "comment-count" vrednosti
            "comment" - čvor koji je dete čvora "comment-list", predstavlja pojedinačni komentar, i ima atribut "comment-id" - string koji predstavlja ID komentara u stablu komentara. Komentari prvog nivoa će imati kao ID proste integere - "1", "2", itd. Ako neko npr. odgovori na 2. komentar prvog nivoa, i time započne thread, taj odgovor će imati ID "2-1", a komentari u tom threadu će imati ID u obliku "2-X", gde je X redni broj komentara u tom threadu. Na nekim sajtovima je moguće da u okviru postojećeg threada nastane subthread, u tom slučaju se i ID proširuje dodatnim crticama. Na primer, ako u posmatranom threadu iz primera neko odgovori na 4. komentar i njime otvori nov thread, ID tog odgovora će biti "2-4-1". "comment" čvor ima sledeće čvorove-listove:
                - "comment-parent-id" - string koji predstavlja ID komentara-roditelja posmatranog komentara u stablu komentara, dobijen na gorenavedeni način. Ako se radi o top-level komentaru, onda je ovaj string prazan.
                - "comment-text" - string koji sadrži tekst komentara
                - "comment-text-transliterated" - string koji sadrži tekst komentara presloveljen na latinicu. Kao i za članke, u praksi će ovo biti bitno tj. različito od "comment-text" pre svega za sajtove na srpskom gde se mogu javiti komentari na ćirilici.
'''

portali = {'blic': '02',
           'kurir': '03',
           'danas': '04',
           'alo': '05',
           'novosti': '06',
            'b92': '07',
            'srbijadanas': '08'}

file = open('/Users/lenka/Desktop/spisak.txt', encoding='utf-8')
pretraga = file.read().split('\n')


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


# extract_danas(url_danas)
#article = extract_danas(url_danas)
#pack_xml(article, '01')

#article = extract_alo(alo_url)
#pack_xml(article, '01')
scrapper_alo()