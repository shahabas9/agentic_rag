import asyncio
from playwright.async_api import async_playwright

# Read URLs from file
with open("loaded_support_article_links.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(urls)} URLs from file")

async def scrape():
    all_docs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # set headless=False to see browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for i, url in enumerate(urls, 1):
            try:
                await page.goto(url, timeout=30000)  # wait 30s
                await page.wait_for_timeout(5000)    # wait 5s for JS
                text = await page.inner_text("body")
                all_docs.append({"url": url, "content": text})
                print(f"[{i}/{len(urls)}] ✅ Scraped: {url} (length={len(text)})")
            except Exception as e:
                print(f"[{i}/{len(urls)}] ❌ Failed: {url} | Error: {e}")

        await browser.close()

    print(f"\nTotal documents scraped: {len(all_docs)}")
    # Save to file
    with open("scraped_articles.txt", "w", encoding="utf-8") as f:
        for doc in all_docs:
            f.write(f"URL: {doc['url']}\n")
            f.write(f"CONTENT:\n{doc['content']}\n")
            f.write("="*80 + "\n")

asyncio.run(scrape())
