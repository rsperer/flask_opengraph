import json
import logging
from datetime import datetime

from bs4 import BeautifulSoup
import requests
from opengraph_parse import parse_page

from flaskog import db
from flaskog.models import OGP


def get_canonical(page_url: str) -> str:
    response = requests.get(page_url)
    if response.status_code is not 200:
        return page_url

    soup = BeautifulSoup(response.content, 'html.parser')
    canonical = soup.find("link", rel="canonical")
    if canonical:
        value = canonical["href"]
        return value

    canonical = soup.find("meta", property="og:url")
    if canonical:
        value = canonical["content"]
        return value

    return page_url


def scrape_og_tags(url, url_id):
    record = OGP.query.filter_by(url_id=url_id).first()
    if not record:
        return
    content = {"id": str(url_id), "url": url}
    image = {}
    og_tags = parse_page(url)
    if og_tags:
        # convert og tags to our tags
        for key, value in og_tags.items():
            clean_key = key.replace("og:", "")
            if clean_key == "image":
                image["url"] = value
            elif clean_key.startswith("image"):
                image[clean_key.replace("image:", "")] = value
            else:
                content[clean_key] = value
        if image:
            content["images"] = [image]
        content["scrape_status"] = "done"
    else:
        content["scrape_status"] = "error"
    content["updated_time"] = str(datetime.now())
    record.json = json.dumps(content, default=str)
    db.session.commit()