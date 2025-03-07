from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
import re 

url = "https://www.bbb.org/us/ny/new-york/profile/pet-supplies/barkbox-0121-143591/customer-reviews"

def scrape_reviews(page_content):
    """Scrape reviews from the given page content."""
    soup = BeautifulSoup(page_content, "html.parser")
    review_list = soup.find_all('li', class_="card")

    data = []
    for i in range(0, len(review_list)):
        try:
            name = (
                review_list[i].find('div', class_='review-grid dtm-review')
                .find('div', attrs={'data-area': 'name'})
                .find('h3').get_text()
            )
            match = re.search(r'(?<=^Review from )(.+)', name)
            name = match.group(0) if match else name      
            star_rating = (
                review_list[i].find('div', class_='review-grid dtm-review')
                .find('div', attrs={'data-area': 'rating'})
                .find('span', class_='visually-hidden').get_text(strip=True)
            )
            date = (
                review_list[i].find('div', class_='review-grid dtm-review')
                .find('div', attrs={'data-area': 'date'})
                .find('p').get_text(strip=True)
            )
            review_text = (
                review_list[i].find('div', class_='review-grid dtm-review')
                .find('div', attrs={'data-area': 'review'})
                .find('div').get_text(strip=True)
            )
            
            data.append({
                "Name": name,
                "Star Rating": star_rating,
                "Date": date,
                "Review": review_text
            })
        except AttributeError:
            continue  # Skip if any field is missing

    return data

with sync_playwright() as p:
    browser = p.webkit.launch(headless=True, slow_mo=50)
    page = browser.new_page()
    page.goto(url)

    # Scrape initially displayed reviews
    all_reviews = scrape_reviews(page.content())

    # Load more reviews if the button still exists
    while True:
        try:
            load_more_button = page.get_by_role("button", name="Load More")
            if load_more_button.is_visible():
                load_more_button.click()
                print("Clicked Load More...")
                sleep(2)  # Allow time for more reviews to load
                new_reviews = scrape_reviews(page.content())

                if new_reviews:
                    all_reviews.extend(new_reviews)
                else:
                    break  # No new reviews detected, exit loop
            else:
                print("No more Load More button to click.")
                break
        except Exception as e:
            print("Error:", e)
            break

    browser.close()


df = pd.DataFrame(all_reviews)
df.to_csv("barkbox_bbb_reviews.csv", index=True)

print("Scraping completed. CSV saved as 'barkbox_bbb_reviews.csv'.")
