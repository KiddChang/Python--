import pymongo
import requests
from bs4 import BeautifulSoup
import json
ss = requests.session()
# information for mongodb atlas or local server
conn_str = "mongodb://tfb1031:qwe123456@10.2.16.174/raw_data_for_project"  # local server
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
db = client.get_database('raw_data_for_project')
collection = db.ifoodie
mongo_index_id = 0

tmpData = list()

page = 1
url= "https://ifoodie.tw/explore/%E5%AE%9C%E8%98%AD%E7%B8%A3/list?page={}".format(page)
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
headers = {'User-Agent': userAgent}

for Page1 in range(1,68):

    res = requests.get(url, headers=headers)
    ifoodie_html = BeautifulSoup(res.text,'html.parser')

    for j, i in enumerate(ifoodie_html.select('a[target="_self"]')):
        if j % 3 == 0:
            articleUrl = 'https://ifoodie.tw' + i['href']
            # print(articleUrl)

            resnew = requests.get(articleUrl, headers=headers)
            soupnew = BeautifulSoup(resnew.text, 'html.parser')
            try:
                imgurl = soupnew.select('img[class="jsx-307016528 cover"]')  # 店圖位置
                commentinfo = soupnew.select('a[class="jsx-307016528"]')
                commentpoint = (soupnew.select('div[class="jsx-1207467136 text"]'))
                Detail = soupnew.select('span[class="jsx-1692663080 detail"]')
                Shop_name = commentinfo[0].text  # 店名 變數
                add = Detail[0].text  # 住址 變數
                Point = commentpoint[0].text  # 評分 變數
                Commentcount = commentinfo[1].text  # 評論數變數
                Ave_consumption = Detail[1].text  # 均消 變數
                image = imgurl[1]['src']  # 店圖 變數
                print(image)  # 店圖
                # print(Shop_name)  # 店名
                # print(add)  # 住址
                # print(Point)  # 評分
                # print(Commentcount)  # 評論數
                # print(Ave_consumption)  # 均消

                comment = str(soupnew.select('script[class="next-head"]')[12]).replace(
                    '<script class="next-head" type="application/ld+json">', '').replace('</script>', '')
                # print(comment)
                comments = json.loads(comment)
                tmpstr = list()
                for Com in comments["review"]:
                    Com_comment = Com['description']  # 評論
                    tmpstr.append(Com_comment)
                    # print(Com_comment)

                tmpDict_for_mongo = {

                    'Shop_name': Shop_name,
                    'address': add,
                    'Point': Point,
                    'Commentcount': Commentcount,
                    'Ave_consumption': Ave_consumption,
                    'articleUrl': articleUrl,
                    'Com_comment': tmpstr,
                    'image': image
                }
                mongo_index_id += 1
                tmpData.append(tmpDict_for_mongo)
                print('=========')
            except IndexError:
                pass

    url = "https://ifoodie.tw/explore/%E5%AE%9C%E8%98%AD%E7%B8%A3/list?page={}".format(Page1)
    print(Page1)

collection.insert_many(tmpData)
print('data counts =', collection.count_documents({}))