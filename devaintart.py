# encoding in utf-8

# API for pytohn ref: https://neighbordog.github.io/deviantart/reference.html
# https://neighbordog.github.io/deviantart/index.html
# deviation object ref(Official):https://www.deviantart.com/developers/http/v1/20160316/object/deviation

# import deviantart library
import deviantart
import csv
import os
import re
import requests
import time
import datetime
from multiprocessing import Pool
#from pprint import pprint

def parsejobs(deviation):
	# create an API object with your client credentials
	da = deviantart.Api("", "") # YOUR_CLIENT_ID, YOUR_CLIENT_SECRET
	# the name of the user we want to fetch deviations from
	__username__ = ""

	image_path = './{}/'.format(__username__)

	da_appurl = deviation.deviationid

	if(deviation.is_deleted):
		print('[ ! ] The post had been deleted!')
		return
	if(deviation.published_time):
		readableTime = datetime.datetime.fromtimestamp(deviation.published_time).isoformat()
		readableTime = re.search(r'(.+)T', readableTime).group(1)
	else:
		readableTime = 'withoutDateTime'
	if(deviation.is_downloadable == False):
		try:
			imageDownloadUrl = deviation.content['src']
			regexSearch = re.search(r"https:\/\/.+net(.+)\/(.+)", imageDownloadUrl)
			date = regexSearch.group(1)
			date = re.sub(r"\/", '-', date)
			imageNameWithoutPath = 'deviantart-{0}-{1}-{2}'.format(readableTime, date, regexSearch.group(2))
			img_data = requests.get(imageDownloadUrl).content
			image_name = image_path + imageNameWithoutPath
			
			if (os.path.isfile(image_name)):
				print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
				return
			print('[ ! ] This image\'s quality may not be well, beacuse the author blocked the download option.')
			print('[✓] donwloading {}'.format(imageNameWithoutPath))
			with open(image_name, 'wb') as handler:
				handler.write(img_data)
		except:
			return
	imageInfo = da.download_deviation(da_appurl)

	
	regexSearch = re.search(r"https:\/\/s3.amazonaws.com\/.+deviantart.net\/(.+)\/(.+)\?", imageInfo['src'])
	imageDownloadUrl = regexSearch.group()[:-1]
	date = regexSearch.group(1)
	date = re.sub(r"\/", '-', date)
	imageNameWithoutPath = 'deviantart-{0}-{1}-{2}'.format(readableTime, date, regexSearch.group(2))

	img_data = requests.get(imageDownloadUrl).content

	image_name = image_path + imageNameWithoutPath

	if (os.path.isfile(image_name)):
		print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
		return
	print('[✓] donwloading {}'.format(imageNameWithoutPath))
	with open(image_name, 'wb') as handler:
		handler.write(img_data)

def get_cursor( _username):
	#global session
	#plurk = _session
	#global da
	#plurk = _da
	global __username__
	__username__ = _username

	
if __name__ == "__main__":
	t1 = time.time()

	# create an API object with your client credentials
	da = deviantart.Api("", "")  # YOUR_CLIENT_ID, YOUR_CLIENT_SECRET
	# the name of the user we want to fetch deviations from
	crawlUserName = ""
	
	# define defaults
	deviations = []

	offset = 0
	has_more = True
	
	path = './' + crawlUserName
	if not os.path.exists(path):
		os.mkdir(path)
	
	# while there are more deviations to fetch
	while has_more:

		try:
			# fetch deviations from user
			fetched_deviations = da.get_gallery_folder(
				username=crawlUserName,
				offset=offset
			)
			#print(type(fetched_deviations))
			#print((fetched_deviations))

			# add fetched deviations to stack
			deviations += fetched_deviations['results']

			# update offset
			offset = fetched_deviations['next_offset']

			# check if there are any deviations left that we can fetch (if yes => repeat)
			has_more = fetched_deviations['has_more']

		except deviantart.api.DeviantartError as e:
			# catch and print API exception and stop loop
			print(e)
			has_more = False
	t2 = time.time()
	#print("###########################\n")
	print(len(deviations))
	
	
	csvName = '{}.csv'.format(crawlUserName)
	with open(csvName, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow([crawlUserName])
		writer.writerow(['Date','Url','Title','Downloadable','filesize_download','filesize_content-src','content-src'])
		writer = csv.writer(csvfile, delimiter=',')
		for deviation in deviations:
			_readableTime = datetime.datetime.fromtimestamp(deviation.published_time).isoformat()
			_date = re.search(r'(.+)T', _readableTime).group(1)
			writer.writerow( [ _date,deviation.url,deviation.title,deviation.is_downloadable,deviation.download_filesize,deviation.content['filesize'],deviation.content['src'] ] )

	t3 = time.time()

	pool = Pool()
	pool.map_async(parsejobs, deviations)
	pool.close()
	pool.join()
	
	poolTime = time.time() - t3
	total_time = time.time() - t1

	apiLoopTime = t2 - t1
	writeCsvTime = t3 - t2
	print("\nAPI Loop Time: {}\n".format(apiLoopTime))
	print("Write Csv Time: {}\n".format(writeCsvTime))
	print("Pool Time: {}\n".format(poolTime))
	print("Total Time: {}\n".format(total_time))

