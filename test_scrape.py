import requests
from bs4 import BeautifulSoup
import re

url = "https://asuri.ru/mb/index.php/rassylki/243-213-mekhanizm-obshcheniya"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the main content div
content = soup.find("div", itemprop="articleBody") or soup.find("div", class_="item-page") or soup.find("div", id="content")
if content:
    print("Found content container:", content.name, content.attrs)
    # print first 500 chars of text
    print(content.text[:500])
else:
    print("Could not find a standard content container. Available divs:")
    for div in soup.find_all("div")[:10]:
        print(div.attrs)
