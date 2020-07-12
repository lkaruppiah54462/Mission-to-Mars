# Import Splinter and BeautifulSoup
import pandas as pd
import datetime as dt
from splinter import Browser
from bs4 import BeautifulSoup as Soup

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="..\\webscrapping\\chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    hemisphere_images,hemisphere_names = mars_hemisphere_images(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_image_0" : hemisphere_images[0],
        "hemisphere_names_0" : hemisphere_names[0],
        "hemisphere_image_1" : hemisphere_images[1],
        "hemisphere_names_1" : hemisphere_names[1],
        "hemisphere_image_2" : hemisphere_images[2],
        "hemisphere_names_2" : hemisphere_names[2],
        "hemisphere_image_3" : hemisphere_images[3],
        "hemisphere_names_3" : hemisphere_names[3],                        
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=2)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = Soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

# ### Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = Soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

# ###  MARS FACTS

def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemisphere_images(browser):
    #empty list for image and text link
    high_res_image_link = []
    image_title = []

    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    hem_images_link = browser.find_by_tag("h3")

    #loop through splinter to extract the image links
    for images in range(len(hem_images_link)):
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
        hem_images_link = browser.find_by_tag("h3")
        hem_images_link[images].click()
        browser.is_element_present_by_text('Hemisphere',wait_time = 2)
        #t.sleep(2)
        # Find and click the open full image
        full_image_elem = browser.find_by_id('wide-image-toggle')
        full_image_elem.click()
        browser.is_element_present_by_text('OPEN',wait_time = 2)
        #t.sleep(2)
        html = browser.html
        hemisphere_soup = Soup(html, 'html.parser')
        try :
            img_rel_link = hemisphere_soup.find('img', class_="wide-image").get('src')
        except AttributeError:
            img_rel_link = None
 
        try:
            header_text = hemisphere_soup.find('h2', class_="title").get_text()
        except AttributeError:
            header_text = None

        img_link = f'https://astrogeology.usgs.gov{img_rel_link}'
        high_res_image_link.append(img_link)    
        image_title.append(header_text)  

    return high_res_image_link,image_title

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())




