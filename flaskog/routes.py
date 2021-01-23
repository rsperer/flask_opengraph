import logging
import threading

from flask import request
from flaskog import app
from flaskog.models import *
from flaskog.og_parse import parse_page
import json


@app.route("/")
def hello():
    return "<h1>Hello Me!</h1>"


def get_canonical(input_url: str):
    return input_url


@app.route("/stories", methods=["POST"])
def add_or_get_canonical_url_id():
    input_url = request.args.get("some_url", None)
    existing_url = URL.query.filter_by(url=input_url).first()
    if existing_url:
        record = Canonical.query.filter_by(canonical_url=existing_url.canonical_url).first()
        if record:
            return str(record.id)
        else:
            return input_url
    else:
        canonical_url = get_canonical(input_url)
        canonical = Canonical(canonical_url=canonical_url)
        db.session.add(canonical)
        db.session.add(URL(url=input_url, canonical_url=canonical_url))
        db.session.commit()
        return str(canonical.id)


@app.route("/stories/<int:url_id>", methods=["GET"])
def scrape_url_id(url_id: int):
    url = Canonical.query.get_or_404(url_id)
    ogp = OGP.query.filter_by(url_id=url_id).first()
    if ogp:
        return ogp.json
    # This is the first time we've been asked to scrape this URL
    content = {"id": str(url_id), "url": url.canonical_url, "scrape_status": "pending"}
    json_response = json.dumps(content, default=str)
    db.session.add(OGP(url_id=url_id, json=json_response))
    db.session.commit()
    threading.Thread(target=scrape_og_tags, args=(url.canonical_url, url_id,)).start()
    return json_response


def scrape_og_tags(url, url_id):
    logging.info(f"start scraping {url}")
    record = OGP.query.filter_by(url_id=url_id).first()
    if not record:
        return
    content = {"id": str(url_id), "url": url}
    og_tags = parse_page(url)
    if og_tags:
        # convert og tags to our tags
        for key, value in og_tags.items():
            clean_key = key.replace("og:", "")
            content[clean_key] = value
        content["scrape_status"] = "done"
    else:
        content["scrape_status"] = "error"
    record.json = json.dumps(content, default=str)
    db.session.commit()
    logging.info(f"saving {url}")
