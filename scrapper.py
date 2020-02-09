import xml.etree.cElementTree as ET
import cyrtranslit



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
    print(article_code)
    tree.write('/Users/lenka/Desktop/'+portal+'end/'+file, encoding='utf-8')




