import uuid

def generate_config():
    with open('student_id.txt', encoding='utf-8') as f:
        student = f.read().strip()
    student_id = f"{student}_{uuid.uuid4().hex[:8]}"
    content = f'''STUDENT_ID = "{student_id}"
SOURCES    = [
"https://www.japantimes.co.jp/feed/",
"https://rss.dw.com/xml/rss-en-world",
"http://feeds.foxnews.com/foxnews/world",
"https://www.usatoday.com/rss/news/",
"https://www.cbsnews.com/latest/rss/world",
"https://www.ft.com/?format=rss",
"https://apnews.com/apf-topnews?format=rss",
"http://feeds.washingtonpost.com/rss/world",
"https://feeds.npr.org/1001/rss.xml",
"https://www.theguardian.com/world/rss",
]
'''
    with open('config.py', 'w', encoding='utf-8') as cfg:
        cfg.write(content)

if __name__ == '__main__':
    generate_config()
