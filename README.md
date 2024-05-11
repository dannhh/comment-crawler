# Comment Crawler

This project is a comment crawler for various products on Tiki.vn. It uses the aiohttp and asyncio libraries for asynchronous HTTP requests and BeautifulSoup for parsing HTML.

## Installation 

Clone the repository and install the required packages:

```bash 
  git clone https://github.com/dannhh/comment-crawler
  cd comment-crawler
  pip install -r requirements.txt
```

## Usage
Run the `app.py` script:
```
python app.py
```
This will start the comment crawler. The script will send HTTP requests to the Tiki.vn API to fetch product data and reviews, and save them to a file.

## Data
The script saves the product data and reviews to the following files:

- product_ids.txt: Contains the IDs of the products.
- products.txt: Contains the product data in JSON format.
- products.csv: Contains the product data in CSV format.