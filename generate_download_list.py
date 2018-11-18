import requests
from requests import Request, Session
import urllib
import json
import bs4 as bs
import re
import time

import toolkit_sqlite
import config

QUERY_URL = 'https://y2mate.com/analyze/ajax'
VIDEO_LIST = 'youtube_video.list'


def read_video_list():
    with open(VIDEO_LIST, 'r') as f:
        videoList = f.read().split('\n')
    return videoList


def get_best_download_link(htmlPage):
    '''Get the best quality video from download table'''
    soup = bs.BeautifulSoup(htmlPage, 'lxml')
    tbl = soup.table

    # print(tbl.findAll("tr"))
    records = []
    for tr in [i for i in tbl.findAll("tr") if len(i.findAll("td")) == 3]:
        # print(tr)
        # print('+'*80)
        record = dict()
        resolution_tag, size, dl_link = tr.findAll("td")
        if dl_link.a.attrs['href'].startswith('http'):
            record['resolution'] = int(
                resolution_tag.text.strip().split('p')[0])
            record['link'] = dl_link.a.attrs['href']
            record['name'] = dl_link.a.attrs['download']
            record['size'] = size
            records.append(record)

    selected_link = max(records, key=lambda x: x['resolution'])
    return selected_link


def query_link_generate(youtube_link):
    '''
    youtube_link = 'https://www.youtube.com/watch?v=iAzShkKzpJo'
    '''
    data = 'url={}&ajax=1'.format(urllib.parse.quote_plus(youtube_link))
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://y2mate.com",
        "referer": "https://y2mate.com/youtube/Xi52tx6phRU",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    Sess = requests.session()
    req = Request('POST', QUERY_URL, data=data, headers=headers)
    prepped = Sess.prepare_request(req)
    resp = Sess.send(prepped)
    resp_text = resp.content.decode('utf-8')

    # print(data)
    # print(resp_text)
    result = json.loads(resp_text)

    video_dict = get_best_download_link(result["result"])
    return video_dict


if __name__ == '__main__':
    # test_link = 'https://www.youtube.com/watch?v=f4KOjWS_KZs'
    # query_link_generate(test_link)

    # videoDownloadLinkList = list(map(query_link_generate, read_video_list()))

    print('Count of videos to be downloaded: {}'.format(len(read_video_list())))
    count = 1

    with toolkit_sqlite.SqliteDB(config.DB_FILE) as db:
        truncate_sql = '''DELETE FROM download_status;'''
        db.execute(truncate_sql)

        for originalLink in read_video_list():
            video_info = query_link_generate(originalLink)
            print('{}/{} Got {}: {}p'.format(count, len(read_video_list()),
                                             video_info['name'], video_info['resolution']))
            insert_sql = '''INSERT INTO download_status (
                                id,
                                video_name,
                                resolution,
                                size,
                                download_link,
                                original_link,
                                status
                            )
                            VALUES (
                                '{id}',
                                '{video_name}',
                                '{resolution}',
                                '{size}',
                                '{download_link}',
                                '{original_link}',
                                '{status}'
                            );'''.format(id=count, video_name=video_info['name'], original_link=originalLink,
                                         download_link=video_info['link'], resolution=video_info['resolution'], size=video_info['size'], status='PENDING')
            db.execute(insert_sql)

            time.sleep(1)
            count += 1
