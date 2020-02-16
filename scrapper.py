import xml.etree.cElementTree as ET
import cyrtranslit
import os
import xml.etree.ElementTree as ET


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

    if portal in portali:
        article_code = 'sr-'+portali[portal]+'-'+str(id)
    else:
        article_code = 'sr-'+portal+'-'+str(id)

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
    for comment_id in article['comments']:
        comment_el = ET.SubElement(comment_list, "comments")
        comment_el.set('comment-id', comment_id)

        parent_id = 'empty'
        if '-' in str(comment_id):
            parent_id = str(comment_id).split('-')[0]
        #print('parent id ',parent_id)

        ET.SubElement(comment_el, "comment-parent-id").text = parent_id
        ET.SubElement(comment_el, "comment-text").text = article['comments'][comment_id]
        ET.SubElement(comment_el, "comment-text-transliterated").text = cyrtranslit.to_latin(article['comments'][comment_id])

        i+=1

    tree = ET.ElementTree(root)
    file = article_code+".xml"
    #print(article_code)
    tree.write('/Users/lenka/Desktop/'+portal+'/'+file, encoding='utf-8')


def analyze_sort_xml(folder):
    '''
    Analyze year count and comment number
    Check for duplicates
    Sort alphabetically per title
    '''

    titles = {}
    year_counter = {'2015':0, '2016':0, '2017':0, '2018':0,'2019':0, '2020':0}

    total = 0

    for filename in os.listdir(folder):
        if filename.endswith(".xml"):


            #print(filename)
            article_id = filename.split('.')[0]
            filepath = folder+'/'+filename

            root = ET.parse(filepath).getroot()

            title = root.find('article').find('article-title').text.replace('&quot;','')\
                .replace('è','č').replace('æ','ć').replace('ð','đ').replace('&amp;#x201c;','')

            if title.startswith(':'):
                title = title[3:]

            if title.endswith('\n'):
                title = title[:-2]

            if not title.endswith('"'):
                continue

            if title.startswith(' '):
                title = title[1:]

            if title in titles:
                print('duplicate ', article_id, title)
                continue

            titles[title] = article_id

            date = root.find('article').find('article-time').text
            if '.' in date:
                year = date.split('.')[2]
            else:
                year = date.split('-')[0].strip()
                if len(year)==2:
                    year = date.split('-')[2].strip()

            if year not in year_counter:
                print('incorrect year ',year, article_id)
            else:
                year_counter[year]+=1

            total += 1

            #print(root.find('comments').find('comment-count').text)

        else:
            continue

    index = 1
    for title in sorted(titles):
        print(title, titles[title], str(index))


        sorted_folder = folder+'sorted'

        #print(sorted_folder)

        filepath = folder + '/' + titles[title]+'.xml'
        #print(filepath)
        root = ET.parse(filepath).getroot()
        tree = ET.ElementTree(root)

        ET.SubElement(root, "local-id").text = str(index)

        tree.write(sorted_folder+'/sr-'+root.find('source-id').text+'-'+str(index)+'.xml', encoding = 'utf-8')
        index+=1

    print(year_counter)
    print('total ', total)

analyze_sort_xml('/Users/lenka/Desktop/b92final')