import requests
import os

import toolkit_file
import toolkit_sqlite
import config


VIDEO_LIST = 'youtube_video_download.list'
proxy = '127.0.0.1:1080'
downloadPath = 'download/'

toolkit_file.create_folder(downloadPath)


def remove_illegal_char(fileName):
    '''
    Remove reserved characters from file name
    '''
    RESERVED_CHAR = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ]

    for char in RESERVED_CHAR:
        fileName = fileName.replace(char, '_')
    return fileName


def read_list():
    with toolkit_sqlite.SqliteDB(config.DB_FILE) as db:
        query_sql = '''SELECT id||'_'||video_name, download_link, id FROM download_status WHERE status <> 'COMPLETED';'''
        return db.query(query_sql)


def update_status(_id, status):
    with toolkit_sqlite.SqliteDB(config.DB_FILE) as db:
        update_sql = '''UPDATE download_status
                            SET status = '{status}' WHERE id = '{id}';'''.format(id=_id, status=status)
        db.execute(update_sql)


def download_file(fileName, url):
    '''
    Download file with proxy
    '''
    try:
        proxies = {'http': 'http://{}'.format(proxy),
                   'https': 'https://{}'.format(proxy)}
        res = requests.get(url, proxies=proxies)
        con = res.content
        with open(fileName, 'wb') as f:
            f.write(con)
    except Exception as e:
        print('Downloading failed')
        raise
    else:
        print('Downloading finished')
    finally:
        pass


if __name__ == '__main__':
    for fileName, download_link, _id in read_list():
        try:
            print('Downloading ' + fileName)
            update_status(_id, 'DOWNLOADING')
            download_file(downloadPath + fileName, download_link)
        except Exception as e:
            status = 'FAILED'
        else:
            status = 'COMPLETED'
        finally:
            update_status(_id, status)
