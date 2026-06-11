import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime

target_url = "https://www.fa.gov.tw/list.php?theme=FisheriesAct_RULE&subtheme="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response = requests.get(target_url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

fg = FeedGenerator()
fg.id(target_url)
fg.title('漁業署-漁業法規更新')
fg.author({'name': 'RSS Bot'})
fg.link(href=target_url, rel='alternate')
fg.description('自動監控漁業署法規公告網頁的 RSS Feed')

items_found = 0
# 尋找所有帶有超連結的 a 標籤
for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    title = a_tag.get_text(strip=True)
    
    # 條件：標題長度>5 (過濾掉短按鈕)、不能是回到列表頁(list.php)、網址內含 id 或 view
    if len(title) > 5 and 'list.php' not in href and ('id=' in href or 'view.php' in href):
        # 組裝完整網址
        if not href.startswith('http'):
            link = 'https://www.fa.gov.tw/' + href.lstrip('/')
        else:
            link = href
            
        # 檢查是否已經加過這個連結（避免同一篇文章的圖片和標題重複加入）
        existing_links = [entry.link()[0]['href'] for entry in fg.entry()]
        if link not in existing_links:
            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(datetime.datetime.now(datetime.timezone.utc))
            items_found += 1
            
    # 抓取最新 10 筆就好
    if items_found >= 10:
        break

fg.rss_file('fisheries_rules.xml', pretty=True)
print(f"成功！總共抓取了 {items_found} 筆法規更新。")
