import requests
import pandas as pd

url = "https://support.loaded.com/api/v2/help_center/en-gb/articles.json"
articles = []

while url:
    r = requests.get(url)
    data = r.json()
    for art in data["articles"]:
        articles.append({
            "id": art["id"],
            "title": art["title"],
            "url": art["html_url"]
        })
    url = data["next_page"]

# Save to CSV
df = pd.DataFrame(articles)
df.to_csv("loaded_support_articles.csv", index=False)

print(f"Collected {len(articles)} articles. Saved to loaded_support_articles.csv")
