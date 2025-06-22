import urllib.request

url = 'https://www.baidu.com/s?wd='

# 请求对象的定制为了解决反爬虫问题
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
}

name = urllib.parse.quote('周杰伦')
url = url + name

# 请求对象的定制
request = urllib.request.Request(url=url, headers=headers)

response = urllib.request.urlopen(request)


content = response.read().decode('utf-8')

print(content)

print(response.info())

