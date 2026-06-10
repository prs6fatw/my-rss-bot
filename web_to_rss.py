import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime

# 1. 目標網頁網址
target_url = "https://www.fa.gov.tw/list.php?theme=FisheriesAct_RULE&subtheme="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 2. 發送請求並解析網頁
response = requests.get(target_url, headers=headers)
response.encoding = 'utf-8' # 確保中文不亂碼
soup = BeautifulSoup(response.text, 'html.parser')

# 3. 初始化 RSS 產生器
fg = FeedGenerator()
fg.id(target_url)
fg.title('漁業署-漁業法規更新')
fg.author({'name': 'RSS Bot'})
fg.link(href=target_url, rel='alternate')
fg.description('自動監控漁業署法規公告網頁的 RSS Feed')

# 4. 尋找網頁中的法規列表 (根據該網站結構，公告通常在 table 或特定的 class 內)
# 這裡以常見的 <a> 標籤含有法規連結為範例（實務上可根據網頁結構微調）
items_found = 0
for a_tag in soup.find_all('a', href=True):
    # 篩選出可能是文章或法規內容的連結
    if 'detail.php' in a_tag['href']:
        title = a_tag.get_text(strip=True)
        # 補全相對路徑
        link = a_tag['href']
        if link.startswith('detail.php'):
            link = 'https://www.fa.gov.tw/' + link
        
        if title and items_found < 10: # 只取前 10 筆最新的
            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(datetime.datetime.now(datetime.timezone.utc))
            items_found += 1

# 5. 輸出儲存為 RSS XML 檔案
fg.rss_file('fisheries_rules.xml', pretty=True)
print("RSS 檔案轉換成功！")