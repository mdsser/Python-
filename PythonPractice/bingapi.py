import requests
import os

def download_bing_wallpaper():
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    response = requests.get(url)
    json_data = response.json()
    image_url = "https://www.bing.com" + json_data["images"][0]["url"]
    image_name = json_data["images"][0]["enddate"] + ".jpg"
    image_path = os.path.join(os.getcwd(), "bing_wallpaper", image_name)
    if not os.path.exists(os.path.dirname(image_path)):
        os.makedirs(os.path.dirname(image_path))
    response = requests.get(image_url)
    with open(image_path, "wb") as f:
        f.write(response.content)

if __name__ == "__main__":
    download_bing_wallpaper()
