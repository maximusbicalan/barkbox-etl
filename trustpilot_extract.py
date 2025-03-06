from time import sleep 
from random import uniform
from bs4 import BeautifulSoup
import requests 
import pandas as pd

start_page = 1 
end_page = 3 
company_name = "aardy.com"

df_list = []
df = pd.DataFrame(columns=['Name', 'Location', 'Review Heading', 'Review Body', 'Review Date', 'Star Rating'])
for page_index in range(start_page, end_page+1):
    print("Scraping page: ", page_index)

    url = f"https://www.trustpilot.com/review/{company_name}?page={page_index}"

    result = requests.get(url)

    soup = BeautifulSoup(result.content, "html.parser")
    review_cards = soup.find_all('div', class_= "styles_cardWrapper__kOLEb styles_show__qAseP")

    children = list(review_cards) #all 20 children of each page
    for i in range(0, len(children)):
        try:
            child = children[i] # test: get first child of the 20 children
            f_cardInner_header = child.find('article').find('div').find('div', class_="styles_reviewCardInnerHeader__dKkyc")
            
            name = f_cardInner_header.find('aside').find('div').find('a').find('span').get_text()
            location = f_cardInner_header.find('aside').find('div').find('div', class_="styles_consumerExtraDetails__TylYM").find('span').get_text()    
            
            f_stylesReview = child.find('article').find('div').find('section', class_="styles_reviewContentwrapper__Tzamw")
            review_content = f_stylesReview.find('div', class_="styles_reviewContent__SCYfD")
            
            review_h2 = review_content.find('a').find('h2').get_text()
            
            review_body = review_content.find_all('p') #includes review content body and date of experience
            
            review_body_text = review_body[0].get_text() if len(review_body) > 1 else None
            review_date = review_body[1].get_text() if len(review_body) > 1 else review_body[0].get_text()
            star_rating = f_stylesReview.find('div', class_="styles_reviewHeader__PuHBd").find('div').find('img')['alt']

            df_list.append({
                    'Name': name,
                    'Location': location,
                    'Review Heading': review_h2,
                    'Review Body': review_body_text,
                    'Review Date': review_date,
                    'Star Rating': star_rating
                })
            

            print(f"Successfully scraped review: {i} of {name}")
            
            
        except AttributeError as e:
            print(f"Skipping a review due to missing elements on page {page_index}")
            continue
    #avoiding throttling
    sleep(uniform(1.3,6.5))
    print("Failed to scrape page: ", page_index)
df = pd.DataFrame(df_list)

# save to csv
df.to_csv('reviews.csv', index=False)

