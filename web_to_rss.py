import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime

target_url = "https://www.fa.gov.tw/list.php?theme=FisheriesAct_RULE&subtheme="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 加上 timeout 防止連線卡住
response = requests.get(target_url, headers=headers, timeout=15)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

fg = FeedGenerator()
fg.id(target_url)
fg.title('漁業署-漁業法規更新')
fg.author({'name': 'RSS Bot'})
fg.link(href=target_url, rel='alternate')
fg.description('自動監控漁業署法規公告網頁的 RSS Feed')

items_found = 0
seen_links = set() # 【修正】用這個來記錄已經抓過的網址，最安全！

for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    title = a_tag.get_text(strip=True)
    
    # 條件再放寬：只要不是列表頁，且包含 id 或 view 或 article 就可以
    if len(title) > 5 and 'list.php' not in href and ('id=' in href or 'view' in href or 'article' in href):
        if not href.startswith('http'):
            link = 'https://www.fa.gov.tw/' + href.lstrip('/')
        else:
            link = href
            
        if link not in seen_links:
            seen_links.add(link)
            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(datetime.datetime.now(datetime.timezone.utc))
            items_found += 1
            
    if items_found >= 10:
        break

fg.rss_file('fisheries_rules.xml', pretty=True)
print(f"成功！總共抓取了 {items_found} 筆法規更新。")
