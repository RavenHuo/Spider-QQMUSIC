#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  pymysql
import requests
from urllib.parse import urlencode
import json
import time

#连接数据库
conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='1234',db='web_test', use_unicode=True, charset="utf8")
cur=conn.cursor()

#请求头部
header = {'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
               'Connection': 'keep-alive',
               'Referer': 'https://y.qq.com/n/yqq/playlist/1478611135.html'
               }

def get_music():
    parameter = {'picmid': '1',
                 'rnd': '0.25099454148518685',
                 'g_tk': '5381',
                 'jsonpCallback': 'getPlaylist',
                 'loginUin': '0',
                 'hostUin': '0',
                 'format': 'jsonp',
                 'inCharset': 'utf8',
                 'outCharset': 'utf-8',
                 'notice': '0',
                 'platform': 'yqq',
                 'needNewCode': '0',
                 'categoryId': '6',
                 'sortId': '0',
                 'sin': '0',
                 'ein': '100', }
    # 0-29 sin 起始元素 start in ，ein = end in
    url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?' + urlencode(parameter)
    #0-29 sin 起始元素 start in ，ein = end in
    url2='https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?picmid=1&rnd=0.039497698907906664&g_tk=5381&jsonpCallback=getPlaylist&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&categoryId=6&sortId=5&sin=30&ein=59'#30-59
    print(url)
    html=requests.get(url,headers=header)
    html.encoding='utf-8'

    data=json.loads(html.text[12:-1])

    if data and 'data' in data:
        for music_list in data.get('data').get('list'):
            print(music_list)
            dissid=music_list.get('dissid')
            if dissid:
                get_song_mid(dissid)


def get_song_mid(dissid):
    parameter = {'type':'1',
                'json':'1',
                 'utf8':'1',
                 'onlysong':'0',
                 'disstid':str(dissid),
                 'format':'jsonp',
                 'g_tk':'5381',
                 'jsonpCallback':'playlistinfoCallback',
                 'loginUin':'0',
                 'hostUin':'0',
                 'format':'jsonp',
                 'inCharset':'utf8',
                 'outCharset':'utf-8',
                 'notice':'0',
                 'platform':'yqq',
                 'needNewCode':'0' }

    url='https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?'+urlencode(parameter)
    print(url)
    html=requests.get(url,headers=header)
    html.encoding='utf-8'

    data=json.loads(html.text[21:-1])

    if data and 'cdlist' in data:
        for song_list in data.get('cdlist'):
            for song_inf in song_list.get('songlist'):
                #get歌的href
                song_mid=song_inf.get('songmid')
                get_song_inf(song_mid)


def get_song_inf(song_mid):
    time.sleep(0.3)
    parameter = {'songmid':str(song_mid),
                'tpl':'yqq_song_detail',
                'format':'jsonp',
                'callback':'getOneSongInfoCallback',
                'g_tk':'5381',
                'jsonpCallback':'getOneSongInfoCallback',
                'loginUin':'0',
                 'hostUin':'0',
                 'format':'jsonp',
                 'inCharset':'utf8',
                 'outCharset':'utf-8',
                 'notice':'0',
                 'platform':'yqq',
                 'needNewCode':'0'}

    url1='https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?'+urlencode(parameter)
    try:
        html = requests.get(url1, headers=header)
        if html.status_code==200:
            html.encoding = 'utf-8'
            data1 = json.loads(html.text[23:-1])
            if data1 and 'data' in data1:
                song_inf = data1.get('data')[0]
                # get歌的url
                song_mid = song_inf.get('mid')
                song_url = str('https://y.qq.com/n/yqq/song/' + str(song_mid) + '.html')
                print(song_url)

                # get歌名
                song_name = judge(song_inf.get('name'))
                print(song_name)

                # get歌手的名字 加【0】是为了将list转变成dict，接着dict定位name
                singer_name = judge(song_inf.get('singer')[0].get('name'))
                print(singer_name)

                # get歌曲的时长
                if song_inf.get('interval'):
                    song_interval = song_inf.get('interval')
                    song_time_seconds = song_interval % 60
                    song_time_minutes = song_interval // 60  # 取整
                    song_time = str(song_time_minutes) + " : " + str(song_time_seconds)
                else:
                    song_time = 'None'

                # get albummid
                song_albummid = song_inf.get('album').get('mid')
                print(song_albummid)

                if song_albummid:
                    song_inf2 = get_song_inf2(song_albummid)

                    # 歌曲的流派
                    song_genre = song_inf2[0]

                    # 歌曲的语种
                    song_language = song_inf2[1]

                    # 歌曲的发布时间
                    song_public_time = song_inf2[2]
                    print(song_genre)
                    print(song_language)
                    print(song_public_time)
                    try:
                        result = cur.execute(
                    'insert into popular_song(song_name,singer_name,song_url,song_time,song_genre,song_language,song_public_time)values(%s,%s,%s,%s,%s,%s,%s)',(song_name, singer_name, song_url, song_time, song_genre, song_language, song_public_time))

                        # 提交
                        conn.commit()
                        print(result)
                    except Exception as e:
                        print(e)
        else:
            print('connection error')
    except Exception as e:
        print(e)





def get_song_inf2(ablummid):
    song_inf2_list=[]
    parameter = {'albummid':str(ablummid),
                 'jsonpCallback':'getAlbumInfoCallback',
                 'loginUin':'0',
                 'hostUin':'0',
                 'format':'jsonp',
                 'inCharset':'utf8',
                 'outCharset':'utf-8',
                 'notice':'0',
                 'platform':'yqq',
                 'needNewCode':'0'}

    url2 = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?'+urlencode(parameter)
    # 转换成第二个urlget歌曲的流派，语种，发布时间
    try:
        html = requests.get(url2, headers=header)
        if html.status_code == 200:
            html.encoding = 'utf-8'
            print(html.text)
            data2 = json.loads(html.text[22:-1])
            print(data2)
            if data2 and 'data' in data2:
                song_inf2 = data2.get('data')

                # get歌曲的流派
                song_genre = judge(song_inf2.get('genre'))
                song_inf2_list.append(song_genre)

                # get歌曲的语种
                song_language = judge(song_inf2.get('lan'))
                song_inf2_list.append(song_language)

                # get歌曲的发布时间
                song_public_time = judge(song_inf2.get('aDate'))
                song_inf2_list.append(song_public_time)
            return song_inf2_list
        else:
            print('error')
    except Exception as e:
        print(e)

def judge(thing):
    if thing:
        return str(thing)
    else:
        thing='None'
        return thing


if __name__ == '__main__':
    get_music()


