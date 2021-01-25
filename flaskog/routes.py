import threading
from flask import request
from flaskog import app
from flaskog.models import *
from flaskog.og_parse import *
import json

from flaskog.og_parse import scrape_og_tags


@app.route("/stories", methods=["POST"])
def add_or_get_canonical_url_id():
    input_url = request.args.get("some_url", None)
    existing_url_id = db.session.query(Canonical.id).select_from(URL)\
        .join(Canonical).filter(URL.url == input_url).first()
    if existing_url_id:
        return str(existing_url_id[0])
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
    content = {"id": str(url_id), "url": url.canonical_url,
               "scrape_status": "pending", "updated_time": str(datetime.now())}
    json_response = json.dumps(content, default=str)
    db.session.add(OGP(url_id=url_id, json=json_response))
    db.session.commit()
    threading.Thread(target=scrape_og_tags, args=(url.canonical_url, url_id,)).start()
    return json_response

