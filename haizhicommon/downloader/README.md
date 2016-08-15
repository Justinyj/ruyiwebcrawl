### 网页cache的使用：

1.不用网页cache

	DownloadWrapper(None, headers)

2.使用网页cache，cache到s3

	DownloadWrapper('s3', headers, REGION_NAME)

3.使用网页cache，cache到cacheservice

	DownloadWrapper('http://192.168.1.179:8000', headers)
