import re
import os
import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Months mapping for Russian dates
MONTHS = {
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
    'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
    'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
}

def parse_date(date_str):
    try:
        parts = date_str.strip().split()
        if len(parts) == 3:
            day = int(parts[0])
            month = MONTHS[parts[1].lower()]
            year = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception as e:
        print(f"Error parsing date: {date_str} - {e}")
    return date_str

def main():
    base_url = "https://asuri.ru"
    input_file = "/Users/lexone/.cursor/projects/Users-lexone-Documents-Asuri/uploads/rassylki-0.md"
    output_dir = "rassylki"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    articles = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Matching: | [ Title ](/url) | date | views |
            match = re.search(r'\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\s*\|', line)
            if match:
                title = match.group(1).strip()
                url = match.group(2).strip()
                date_str = match.group(3).strip()
                
                # Cleanup title from escaped dots like "213\."
                title = title.replace('\\.', '.')
                
                if not url.startswith('http'):
                    url = base_url + url
                    
                parsed_date = parse_date(date_str)
                
                articles.append({
                    'title': title,
                    'url': url,
                    'date_str': date_str,
                    'parsed_date': parsed_date
                })

    # Sort chronologically (oldest first)
    # The parsed_date is in YYYY-MM-DD format, which sorts correctly as string
    # If parsing failed, we still have the original string (which might not sort perfectly, but we hope parsing works)
    articles.sort(key=lambda x: x['parsed_date'])
    
    print(f"Found {len(articles)} articles.")
    
    for i, article in enumerate(articles, 1):
        print(f"Processing {i}/{len(articles)}: {article['title']}")
        try:
            response = requests.get(article['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find title
            page_title = article['title']
            title_tag = soup.find(itemprop="headline")
            if title_tag:
                page_title = title_tag.text.strip()
                
            # Find content
            content_div = soup.find("div", itemprop="articleBody") or \
                          soup.find("div", class_="com-content-article__body") or \
                          soup.find("div", class_="item-page")
                          
            if content_div:
                # Convert to markdown
                md_content = md(str(content_div), heading_style="ATX")
                
                # Format final content
                final_content = f"# {page_title}\n\n**Дата публикации:** {article['date_str']}\n\n**Источник:** {article['url']}\n\n---\n\n{md_content}"
                
                # Safe filename
                safe_title = re.sub(r'[^\w\s-]', '', article['title']).strip()
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                filename = f"{i:03d}_{safe_title}.md"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(final_content)
            else:
                print(f"Could not find content div for {article['url']}")
                
        except Exception as e:
            print(f"Failed to process {article['url']}: {e}")
            
        time.sleep(0.5) # Be nice to the server
        
if __name__ == "__main__":
    main()
