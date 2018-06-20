import requests
from requests import Request, Session
import urllib, json
import bs4 as bs
import re
import time

QUERY_URL = 'https://y2mate.com/analyze/ajax'
VIDEO_LIST = 'youtube_video.list'


def read_video_list():
	with open(VIDEO_LIST, 'r') as f:
		videoList = f.read().split('\n')
	return videoList


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

	# #mp4 > table > tbody > tr:nth-child(1) > td.txt-center > a
	soup = bs.BeautifulSoup(result["result"], 'lxml')
	videoDownloadLink = soup.select('#mp4 > table > tbody > tr > td.txt-center > a')[0]['href']
	# print(videoDownloadLink)
	videoName = urllib.parse.unquote_plus(re.findall(r'(?<=&title=).*(?=&)', videoDownloadLink)[0]).split(' || ')[0]
	print(videoName)
	return videoName, videoDownloadLink


if __name__ == '__main__':
	# test_link = 'https://www.youtube.com/watch?v=f4KOjWS_KZs'
	# query_link_generate(test_link)
	
	# videoDownloadLinkList = list(map(query_link_generate, read_video_list()))

	count = 1

	with open('youtube_video_download.list', 'w') as f:
		f.write('')

	for i in read_video_list():
		videoName, videoDownloadLink = query_link_generate(i)
		with open('youtube_video_download.list', 'a') as f:
			f.write('{} {} |#| {}\n'.format(count, videoName, videoDownloadLink))
		time.sleep(1)
		count += 1



