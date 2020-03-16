import xml.etree.cElementTree as ET
import cyrtranslit
import os
import xml.dom.minidom as dom
#import xml.etree.ElementTree as ET


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
    root.set('global-id', article_code)


    ET.SubElement(root, "url").text = article['url']
    ET.SubElement(root, "source-id").text = 'sr-'+portali[portal]
    ET.SubElement(root, "local-id").text = str(id)
    ET.SubElement(root, "source-name").text = str.capitalize(portal)
    #ET.SubElement(root, "article")

    article_el = ET.SubElement(root, "article")
    ET.SubElement(article_el, "article-title").text = article['title']
    ET.SubElement(article_el, "article-title-transliterated").text = cyrtranslit.to_latin(article['title'])

    ET.SubElement(article_el, "article-time").text = article['date']
    ET.SubElement(article_el, "article-author").text = article['author']
    ET.SubElement(article_el, "article-text").text = article['text']
    ET.SubElement(article_el, "article-text-transliterated").text = cyrtranslit.to_latin(article['text'])

    comments = ET.SubElement(root, "comments")
    ET.SubElement(comments, "comment-count").text = str(len(article['comments']))
    comment_list = ET.SubElement(comments, "comment-list")

    i = 0
    for comment_id in article['comments']:
        comment_el = ET.SubElement(comment_list, "comment")
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
    year_counter = {'2015':0, '2016':0, '2017':0, '2018':0,'2019':0}

    total = 0

    print(folder)

    for filename in os.listdir(folder):
        if filename.endswith(".xml"):


            print(filename)
            article_id = filename.split('.')[0]


            if len(filename.split('.'))>2:
                article_id = filename.split('.')[0]+'.'+filename.split('.')[1]


            filepath = folder+'/'+filename

            parsed = ET.parse(filepath)

            if not parsed:
                print('not parsed')
                continue

            root = parsed.getroot()

            title = root.find('article').find('article-title').text

            if title.startswith(':'):
                title = title[3:]

            if title.endswith('\n'):
                title = title[:-2]

            #if not title.endswith('"'):
            #     continue

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
                if len(year) == 2:
                    year = date.split('-')[2].strip()

            #if year not in year_counter:
            #    print('incorrect year ',year, article_id)
            #else:
            #    year_counter[year]+=1

            total += 1

            #print(root.find('comments').find('comment-count').text)

        else:
            print('else continue')
            continue

    index = 1
    clean_titles = []
    sorted_folder = folder + 'sorted'

    print('unique ',len(titles))
    for title in sorted(titles):
        print(title, titles[title], str(index))




        #print(sorted_folder)

        filepath = folder + '/' + titles[title]+'.xml'

        print(filepath, titles[title])

        root = ET.parse(filepath).getroot()

        print(root.find('source-id').text)

        title = root.find('article').find('article-title').text.replace('&quot;', '') \
            .replace('è', 'č').replace('æ', 'ć').replace('ð', 'đ').replace('&amp;#x201c;', '').replace('"', '')

        if title in clean_titles:
            print('clean duplicate', title)
            continue

        y = root.find('article').find('article-time').text.split('-')[0]

        print('year ',y, root.find('article').find('article-time').text)

        if int(y)<2000:
            y = root.find('article').find('article-time').text.split('-')[2]

        if y.strip() not in year_counter:
            print('incorrect year ', y, article_id)
            continue
        else:
            year_counter[y.strip()] += 1

        clean_titles.append(title)
        #print(title)

        root.find('article').find('article-title').text =  title

        title_trans = root.find('article').find('article-title-transliterated').text.replace('&quot;', '') \
            .replace('è', 'č').replace('æ', 'ć').replace('ð', 'đ').replace('&amp;#x201c;', '').replace('"', '')


        root.find('article').find('article-title-transliterated').text =  title_trans

        text = root.find('article').find('article-text').text
        clean_text = ''

        if not text or text=="":
            print('no text')
            continue

        print('len',len(text.split('\n')))

        if len(text.split('\n'))>1:
            for row in text.split('\n'):
                # print('row',row)
                if row == 'View this post on Instagram' or '{' in row or '/*' in row or 'A post' in row or 'VIDEO' in row or not row:
                    continue

                if 'srbdan_rs/main' in row:
                    break
                if row.split() and row.split()[0].isupper():
                    continue
                clean_text += row.strip() + ' '
        else:
            clean_text = text

        #print(clean_text)

        root.find('article').find('article-text').text = clean_text.replace('&quot;', '').replace('"', '')


        text = root.find('article').find('article-text-transliterated').text
        clean_text = ''

        for row in text.split('\n'):
            # print('row',row)
            if row == 'View this post on Instagram' or '{' in row or '/*' in row or 'A post' in row or 'VIDEO' in row or not row:
                continue

            if 'srbdan_rs/main' in row:
                break
            if row.split() and row.split()[0].isupper():
                continue
            clean_text += row.strip() + ' '

        #print(clean_text)

        root.find('article').find('article-text-transliterated').text = clean_text.replace('&quot;', '').replace('"', '')


        #tree = ET.ElementTree(root)

        #change local_id instead of adding a new one
        #ET.SubElement(root, "local-id").text = str(index)

        l = root.find('local-id')
        l.text = str(index)


        root.set('global-id', root.find('source-id').text+'-'+str(index))

        if 'global_id' in root.attrib:
            root.attrib.pop('global_id')

        if len(root.findall('local-id'))>1:
            l = root.findall('local-id')[1]
            root.remove(l)
        #del root.attrib['global_id']





        ugly_str = ET.tostring(root)
        dom_xml = dom.parseString(ugly_str)
        pretty_xml = dom_xml.toprettyxml()
        print('SOURCE', root.find('source-id').text)
        file_out = open(sorted_folder+'/'+root.get('global-id')+'.xml', 'w',encoding='utf-8')
        file_out.write(pretty_xml)
        file_out.close()
        #tree.write(sorted_folder+'/sr-'+root.find('global-id')+'.xml', encoding = 'utf-8')


        index+=1

    print('final year counter ',sorted_folder,year_counter)
    print('total ', total)


def repack(folder):
    for filename in os.listdir(folder):
        if filename.endswith(".xml"):

            print(filename)

            article_id = filename.split('.')[0]
            filepath = folder + '/' + filename

            parsed = ET.parse(filepath)

            if not parsed:
                continue

            root = parsed.getroot()

            root.find('source-name').text = root.find('source-name').text.capitalize()

            s_id = root.find('source-id').text
            root.find('source-id').text =  'sr-'+ s_id

            title = root.find('article').find('article-title').text
            print(title)

            trans = ET.Element("article-title-transliterated")
            trans.text =  cyrtranslit.to_latin(title)
            root.find('article').insert(1, trans)


            #comments = ET.Element("comments")
            #comments. root.find('comment-list')
            #root.insert(6, comments)

            comments = root.find("comments")

            #ET.SubElement(comments, "comment-count").text = root.find('comments').find('comment-count').text
            comment_list = ET.SubElement(comments, "comment-list")

            i = 0
            comment_set = []
            for comment in root.find('article').find('comment-list'):
                #print(comment.find('comment-text').text, type(comment))

                comment_text = comment.find('comment-text').text
                print(comment_text)

                if comment_text==None:
                    continue

                if comment_text in comment_set:
                    print('duplicate', comment_text)
                    continue


                comment_el = ET.SubElement(comment_list, "comment")
                comment_id = comment.attrib['comment-id']
                comment_el.set('comment-id', comment_id)

                comment_set.append(comment_text)

                parent_id = 'empty'
                if '-' in str(comment_id):
                    parent_id = str(comment_id).split('-')[0]
                # print('parent id ',parent_id)

                ET.SubElement(comment_el, "comment-parent-id").text = parent_id
                ET.SubElement(comment_el, "comment-text").text = comment_text
                ET.SubElement(comment_el, "comment-text-transliterated").text = cyrtranslit.to_latin(comment_text)

                i += 1

            b = root.find('article').find('comment-list')
            print(b)
            root.find('article').remove(b)

            comments.find('comment-count').text = str(len(comment_set))
            tree = ET.ElementTree(root)
            # print(article_code)
            tree.write(folder + 'repackednew/' + filename, encoding='utf-8')


#analyze_sort_xml('/Users/lenka/Desktop/srbijadanas')
#analyze_sort_xml('/Users/lenka/Desktop/b92')
analyze_sort_xml('/Users/lenka/Desktop/novosti')

#repack('/Users/lenka/Desktop/final/srbijadanas')
#repack('/Users/lenka/Desktop/final/danas')
#repack('/Users/lenka/Desktop/final/alo')
##analyze_sort_xml('/Users/lenka/Desktop/final/b92repackednew')
