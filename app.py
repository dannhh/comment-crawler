import os
import json
import re

import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup

dict_product = {
    "dienthoai": "https://tiki.vn/api/v2/products?q=dien-thoai&page={page}",
    "maytinhbang": "https://tiki.vn/api/v2/products?q=may-tinh-bang&page={page}",
    "banphim": "https://tiki.vn/api/v2/products?q=ban-phim&page={page}",
    "chuotmaytinh": "https://tiki.vn/api/v2/products?q=chuot-may-tinh&page={page}",
    "donghothongminh": "https://tiki.vn/api/v2/products?q=dong-ho-thong-minh&page={page}",
    "tainghe": "https://tiki.vn/api/v2/products?q=tai-nghe&page={page}",
    "laptop": "https://tiki.vn/api/v2/products?q=laptop&page={page}",
    "thietbiluutru": "https://tiki.vn/api/v2/products?q=thiet-bi-luu-tru&page={page}",
    "thietbimang": "https://tiki.vn/api/v2/products?q=thiet-bi-mang&page={page}",
    "linhkienmaytinh": "https://tiki.vn/api/v2/products?q=linh-kien-may-tinh&page={page}",
}

# api
product_api_url = "https://tiki.vn/api/v2/products/{id}"
review_api_url = "https://tiki.vn/api/v2/reviews?product_id={id}"

# file
product_id_file = "product_ids.txt"
product_data_file = "products.txt"
product_file = r"products.csv"
product_data_import_file = "product_data_import.json"
product_data_import_wordpress = "product_data_import_wordpress.csv"
product_id_file = "product_ids.txt"
review_data_file = "reviews.txt"
review_file = r"reviews.csv"
review_data_import_file = "review_data_import.json"
user_data_import_file = "user_data_import.json"

digit = re.compile(r"\d+")
NUM_PAGE = 100

headers = {"user-agent": "my-app/0.0.1", "Content-Type": "application/json"}

schema_product_field = [
    "id",
    "sku",
    "name",
    "short_description",
    "description",
    "price",
    "original_price",
    "breadcrumbs",
    "images",
    "specifications",
]

schema_review_field = ["id", "title", "content", "rating", "created_by", "product_id"]

schema_user_field = [
    "id",
    "name",
    "full_name",
    "region",
    "avatar_url",
    "purchased",
    "purchased_at",
]


async def crawl_product_id():
    product_list = []

    for page_index in range(NUM_PAGE):
        for type_product in dict_product:
            print(f"Product {type_product}: {page_index+1}".format(type_product))

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    dict_product[type_product].format(page=page_index + 1),
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        content = await response.json()
                        list_products = content.get("data")
                        for product in list_products:
                            product_list.append(str(product.get("id")))

    return product_list


def save_product_id(product_list: list):
    with open(product_id_file, "w") as f:
        content = "\n".join(product_list)
        f.write(content)
        f.close()
        print("Save file: ", product_id_file)


async def crawl_product(list_products=[]):
    product_detail_list = []
    for product_id in list_products:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                product_api_url.format(id=product_id), headers=headers
            ) as response:
                if response.status == 200:
                    if "application/json" in response.headers.get("Content-Type", ""):
                        # response.encoding = 'utf-8'
                        # raw = await response.text()
                        # content = raw.replace('\/', '/')
                        content = await response.text()
                        product_detail_list.append(str(content))
                        with open(f"./data/products/{product_id}.json", mode="w+") as file:
                            file.write(str(content))
                            file.close()
                        print("Crawl product: ", product_id, " --> ", response.status)
    return product_detail_list


async def crawl_review(list_products=list()):
    review_detail_list = []
    for product_id in list_products:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                review_api_url.format(id=product_id), headers=headers
            ) as response:
                if response.status == 200:
                    # response.encoding = 'utf-8'
                    # raw = await response.text()
                    # content = raw.replace('\/', '/')
                    content = await response.json()
                    list_reviews = content.get("data")
                    for review in list_reviews:
                        review_detail_list.append(json.dumps(review))
                        review_id = review.get("id")
                        with open(
                            f"./data/reviews/{review_id}.json", mode="w+"
                        ) as file:
                            file.write(str(review))
                            file.close()
                        print("Crawl review: ", review_id, " --> ", response.status)
    return review_detail_list


def field_filter_product(obj, schema_field):
    e = json.loads(obj)
    if not e.get("id", False):
        return None

    p = dict()

    for field in schema_field:
        if field in e:
            p[field] = e.get(field, False)

    return p


def field_filter_review(obj, schema_field):
    e = json.loads(obj)
    if not e.get("id", False):
        return None

    p = dict()

    for field in schema_field:
        if field in e:
            if field == "created_by":
                p[field] = e["created_by"]["id"]
            else:
                p[field] = e.get(field, False)

    return p


def field_filter_user(obj, user, schema_field):
    e = json.loads(obj)
    if not e.get("id", False):
        return None

    p = dict()

    for field in schema_field:
        if field in e[user]:
            p[field] = e[user].get(field, False)

    return p


def save_raw(product_detail_list=[], file_path=""):
    with open(file_path, "w+") as f:
        content = "\n".join(product_detail_list)
        f.write(content)
        f.close()
        print("Save file: ", file_path)


def save_json(item_json_list, file_path):
    with open(file_path, mode="w") as f:
        f.write(json.dumps(item_json_list))
        f.close()


def save_wordpress(item_json_list, file_path):
    with open(file_path, mode="w") as f:
        wp_string = 'ID@Type@SKU@Name@Published@"Is featured?"@"Visibility in catalog"@"Short description"@Description@"Date sale price starts"@"Date sale price ends"@"Tax status"@"Tax class"@"In stock?"@Stock@"Low stock amount"@"Backorders allowed?"@"Sold individually?"@"Weight(kg)"@"Length(cm)"@"Width(cm)"@"Height(cm)"@"Allow customer reviews?"@"Purchase note"@"Sale price"@"Regular price"@Categories@Tags@"Shipping class"@Images@"Download limit"@"Download expiry days"@Parent@"Grouped products"@Upsells@Cross-sells@"External URL"@"Button text"@Position@"Attribute 1 name"@"Attribute 1 value(s)"@"Attribute 1 visible"@"Attribute 1 global"@"Attribute 1 default"@"Attribute 2 name"@"Attribute 2 value(s)"@"Attribute 2 visible"@"Attribute 2 global"@"Attribute 2 default"@"Attribute 3 name"@"Attribute 3 value(s)"@"Attribute 3 visible"@"Attribute 3 global"@"Attribute 3 default"@"Attribute 4 name"@"Attribute 4 value(s)"@"Attribute 4 visible"@"Attribute 4 global"@"Attribute 4 default"@"Attribute 5 name"@"Attribute 5 value(s)"@"Attribute 5 visible"@"Attribute 5 global"@"Attribute 5 default"@"Attribute 6 name"@"Attribute 6 value(s)"@"Attribute 6 visible"@"Attribute 6 global"@"Attribute 6 default"@"Attribute 7 name"@"Attribute 7 value(s)"@"Attribute 7 visible"@"Attribute 7 global"@"Attribute 7 default"@"Attribute 8 name"@"Attribute 8 value(s)"@"Attribute 8 visible"@"Attribute 8 global"@"Attribute 8 default"@"Attribute 9 name"@"Attribute 9 value(s)"@"Attribute 9 visible"@"Attribute 9 global"@"Attribute 9 default"@"Attribute 10 name"@"Attribute 10 value(s)"@"Attribute 10 visible"@"Attribute 10 global"@"Attribute 10 default"@"Attribute 11 name"@"Attribute 11 value(s)"@"Attribute 11 visible"@"Attribute 11 global"@"Attribute 11 default"@"Attribute 12 name"@"Attribute 12 value(s)"@"Attribute 12 visible"@"Attribute 12 global"@"Attribute 12 default"@"Attribute 13 name"@"Attribute 13 value(s)"@"Attribute 13 visible"@"Attribute 13 global"@"Attribute 13 default"@"Attribute 14 name"@"Attribute 14 value(s)"@"Attribute 14 visible"@"Attribute 14 global"@"Attribute 14 default"@"Attribute 15 name"@"Attribute 15 value(s)"@"Attribute 15 visible"@"Attribute 15 global"@"Attribute 15 default"@"Attribute 16 name"@"Attribute 16 value(s)"@"Attribute 16 visible"@"Attribute 16 global"@"Attribute 16 default"@"Attribute 17 name"@"Attribute 17 value(s)"@"Attribute 17 visible"@"Attribute 17 global"@"Attribute 17 default"@"Attribute 18 name"@"Attribute 18 value(s)"@"Attribute 18 visible"@"Attribute 18 global"@"Attribute 18 default"@"Attribute 19 name"@"Attribute 19 value(s)"@"Attribute 19 visible"@"Attribute 19 global"@"Attribute 19 default"@"Attribute 20 name"@"Attribute 20 value(s)"@"Attribute 20 visible"@"Attribute 20 global"@"Attribute 20 default"@"Attribute 21 name"@"Attribute 21 value(s)"@"Attribute 21 visible"@"Attribute 21 global"@"Attribute 21 default"@"Attribute 22 name"@"Attribute 22 value(s)"@"Attribute 22 visible"@"Attribute 22 global"@"Attribute 22 default"@"Attribute 23 name"@"Attribute 23 value(s)"@"Attribute 23 visible"@"Attribute 23 global"@"Attribute 23 default"@"Attribute 24 name"@"Attribute 24 value(s)"@"Attribute 24 visible"@"Attribute 24 global"@"Attribute 24 default"@"Attribute 25 name"@"Attribute 25 value(s)"@"Attribute 25 visible"@"Attribute 25 global"@"Attribute 25 default"@"Attribute 26 name"@"Attribute 26 value(s)"@"Attribute 26 visible"@"Attribute 26 global"@"Attribute 26 default"@"Attribute 27 name"@"Attribute 27 value(s)"@"Attribute 27 visible"@"Attribute 27 global"@"Attribute 27 default"@"Attribute 28 name"@"Attribute 28 value(s)"@"Attribute 28 visible"@"Attribute 28 global"@"Attribute 28 default"@"Attribute 29 name"@"Attribute 29 value(s)"@"Attribute 29 visible"@"Attribute 29 global"@"Attribute 29 default"@"Attribute 30 name"@"Attribute 30 value(s)"@"Attribute 30 visible"@"Attribute 30 global"@"Attribute 30 default"@"Attribute 31 name"@"Attribute 31 value(s)"@"Attribute 31 visible"@"Attribute 31 global"@"Attribute 31 default"@"Attribute 32 name"@"Attribute 32 value(s)"@"Attribute 32 visible"@"Attribute 32 global"@"Attribute 32 default"@"Attribute 33 name"@"Attribute 33 value(s)"@"Attribute 33 visible"@"Attribute 33 global"@"Attribute 33 default"@"Attribute 34 name"@"Attribute 34 value(s)"@"Attribute 34 visible"@"Attribute 34 global"@"Attribute 34 default"@"Attribute 35 name"@"Attribute 35 value(s)"@"Attribute 35 visible"@"Attribute 35 global"@"Attribute 35 default"@"Attribute 36 name"@"Attribute 36 value(s)"@"Attribute 36 visible"@"Attribute 36 global"@"Attribute 36 default"@"Attribute 37 name"@"Attribute 37 value(s)"@"Attribute 37 visible"@"Attribute 37 global"@"Attribute 37 default"@"Attribute 38 name"@"Attribute 38 value(s)"@"Attribute 38 visible"@"Attribute 38 global"@"Attribute 38 default"@"Attribute 39 name"@"Attribute 39 value(s)"@"Attribute 39 visible"@"Attribute 39 global"@"Attribute 39 default"@"Attribute 40 name"@"Attribute 40 value(s)"@"Attribute 40 visible"@"Attribute 40 global"@"Attribute 40 default"@"Attribute 41 name"@"Attribute 41 value(s)"@"Attribute 41 visible"@"Attribute 41 global"@"Attribute 41 default"@"Attribute 42 name"@"Attribute 42 value(s)"@"Attribute 42 visible"@"Attribute 42 global"@"Attribute 42 default"@"Attribute 43 name"@"Attribute 43 value(s)"@"Attribute 43 visible"@"Attribute 43 global"@"Attribute 43 default"@"Attribute 44 name"@"Attribute 44 value(s)"@"Attribute 44 visible"@"Attribute 44 global"@"Attribute 44 default"@"Attribute 45 name"@"Attribute 45 value(s)"@"Attribute 45 visible"@"Attribute 45 global"@"Attribute 45 default"@"Attribute 46 name"@"Attribute 46 value(s)"@"Attribute 46 visible"@"Attribute 46 global"@"Attribute 46 default"@"Attribute 47 name"@"Attribute 47 value(s)"@"Attribute 47 visible"@"Attribute 47 global"@"Attribute 47 default"@"Attribute 48 name"@"Attribute 48 value(s)"@"Attribute 48 visible"@"Attribute 48 global"@"Attribute 48 default"@"Attribute 49 name"@"Attribute 49 value(s)"@"Attribute 49 visible"@"Attribute 49 global"@"Attribute 49 default"@"Attribute 50 name"@"Attribute 50 value(s)"@"Attribute 50 visible"@"Attribute 50 global"@"Attribute 50 default"'

        for item_json in item_json_list:
            images_string = ""
            for image in item_json["images"]:
                images_string += f"{image['thumbnail_url']},"
            images_string = images_string[:-1]

            attributes_string = ""
            for specification in item_json["specifications"]:
                for attribute in specification["attributes"]:
                    attributes_string += f"@\"{attribute['name']}\"@\"{attribute['value']}\"@\"0\"@\"1\"@\"\""

            breadcrumbs_string = ""
            for breadcrumb in item_json["breadcrumbs"][:-1]:
                breadcrumbs_string += f"{breadcrumb['name']}>"
            breadcrumbs_string = breadcrumbs_string[:-1]

            description_string = (
                item_json["description"].replace("\n", " ").replace("@", " ")
            )
            attributes_string = attributes_string.replace("\n", " ")

            row_string = f"{item_json['id']}@simple@{item_json['sku']}@{item_json['name']}@1@\"0\"@\"visible\"@\"{item_json['short_description']}\"@\"{description_string}\"@\"\"@\"\"@\"taxable\"@\"\"@\"1\"@@\"\"@\"0\"@\"0\"@\"\"@\"\"@\"\"@\"\"@\"1\"@\"\"@\"{item_json['price']}\"@\"{item_json['original_price']}\"@{breadcrumbs_string}@@\"\"@\"{images_string}\"@\"\"@\"\"@@\"\"@@@\"\"@\"\"@0@{attributes_string}"

            wp_string += "\n" + row_string

        f.write(wp_string)
        f.close()


async def main():
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/products", exist_ok=True)
    os.makedirs("./data/reviews", exist_ok=True)
    os.makedirs("./data/users", exist_ok=True)

    product_id_list = await crawl_product_id()
    save_product_id(product_id_list)

    # crawl product and save to file
    # product_list = await crawl_product(product_id_list)
    # save_raw(product_list, product_data_file)

    # product_json_list = [
    #     field_filter_product(p, schema_product_field) for p in product_list
    # ]
    # save_json(product_json_list, product_data_import_file)
    # save_wordpress(product_json_list, product_data_import_wordpress)

    # crawl review and save to file
    review_list = await crawl_review(product_id_list)
    save_raw(review_list, review_data_file)

    review_json_list = [
        field_filter_review(r, schema_review_field) for r in review_list
    ]
    save_json(review_json_list, review_data_import_file)

    user_json_list = [
        field_filter_user(r, "created_by", schema_user_field) for r in review_list
    ]
    save_json(user_json_list, user_data_import_file)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
