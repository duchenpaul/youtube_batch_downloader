import requests
import os


VIDEO_LIST = 'youtube_video_download.list'
proxy = '127.0.0.1:1080'
downloadPath = 'download/'


def remove_illegal_char(fileName):
	'''
	Remove reserved characters from file name
	'''
	RESERVED_CHAR = ['<', '>', ':', '"', '/', '\\', '|', '?', '*',]

	for char in RESERVED_CHAR:
		fileName = fileName.replace(char, '_')
	return fileName

def read_list():
	with open(VIDEO_LIST, 'r') as f:
		downloadList_tmp = f.read().split('\n')

	downloadList = []
	for i in downloadList_tmp:
		# get fileName, downloadUrl
		if not i:
			continue

		downloadItem = i.split(' |#| ')
		downloadItem[0] = remove_illegal_char(downloadItem[0].strip()) + '.mp4'
		downloadList.append(downloadItem)

	return(downloadList)

def download_file(fileName, url):
	'''
	Download file with proxy
	'''
	print('Downloading {}'.format(fileName))
	proxies = {'http': 'http://{}'.format(proxy),
	           'https': 'https://{}'.format(proxy)}
	res = requests.get(url,proxies=proxies)
	con = res.content
	with open(fileName, 'wb') as f:
		f.write(con)
	print('Downloading finished')

def create_download_dir():
	script_dir = os.path.dirname(os.path.realpath(__file__))
	try:
		if downloadPath not in os.listdir(script_dir):
			os.mkdir(downloadPath)
	except FileExistsError as e:
		pass



if __name__ == '__main__':
	create_download_dir()
	for i in read_list():
		download_file(downloadPath + i[0], i[1])
