import requests
from bs4 import BeautifulSoup

# 获取必应首页的HTML代码
url = 'https://www.bing.com/'
response = requests.get(url)
html = response.text

# 使用BeautifulSoup解析HTML代码，获取今日壁纸的图片链接
soup = BeautifulSoup(html, 'html.parser')
img_url = soup.find('div', {'id': 'bgImgProgLoad'})['data-ultra-definition-src']

# 下载图片
response = requests.get(img_url)
with open('bing_wallpaper.jpg', 'wb') as f:
    f.write(response.content)