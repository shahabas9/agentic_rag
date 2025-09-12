import pandas as pd

# Load the CSV
df = pd.read_csv("loaded_support_articles.csv")

# Show total number of articles
print(f"Total articles: {len(df)}")

# Save just the URLs into a text file
df["url"].to_csv("loaded_support_article_links.txt", index=False, header=False)

print("All article links saved to loaded_support_article_links.txt")
