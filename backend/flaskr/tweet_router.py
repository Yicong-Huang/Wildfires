import json
import re
import string

import requests
import rootpath
import twitter
from flask import Blueprint, make_response, jsonify

rootpath.append()
from backend.data_preparation.connection import Connection
from paths import TWITTER_API_CONFIG_PATH
from utilities.ini_parser import parse

bp = Blueprint('tweet', __name__, url_prefix='/tweet')
api = twitter.Api(**parse(TWITTER_API_CONFIG_PATH, 'twitter-API'))


@bp.route("/live_tweet")
def send_live_tweet():
    # TODO: replace source of live tweets to db
    # Simulate request from a mac browser
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/72.0.3626.121 Safari/537.36 '
    }

    query_words = 'fire'  # for now let's use fire for testing

    resp = requests.get(
        f'https://twitter.com/i/search/timeline?f=tweets&vertical=news&q={query_words}%20near%3A\"United%20States'
        f'\"%20within%3A8000mi&l=en&src=typd', headers=headers)

    # Clear all punctuation from raw response body
    tr = str.maketrans("", "", string.punctuation)
    content = str(resp.content)
    content = content.translate(tr)

    id_set = set()
    return_dict = list()
    for id in re.findall("dataitemid(\d+)", content):
        obj = json.loads(str(api.GetStatus(id)))
        if "place" in obj and obj["id"] not in id_set:
            left = obj["place"]['bounding_box']['coordinates'][0][0]
            right = obj["place"]['bounding_box']['coordinates'][0][2]
            center = [(x + y) / 2.0 for x, y in zip(left, right)]
            id_set.add(obj["id"])
            return_dict.append({"lat": center[1], "long": center[0], "id": id})
    resp = make_response(jsonify(return_dict))
    return resp


@bp.route("/tweets")
def send_tweets_data():
    resp = make_response(
        jsonify([{"create_at": time.isoformat(), "long": lon, "lat": lat} for time, lon, lat, _, _ in
                 Connection().sql_execute(
                     "select r.create_at, l.top_left_long, l.top_left_lat, l.bottom_right_long, l.bottom_right_lat "
                     "from records r,locations l where r.id=l.id")]))
    return resp


@bp.route("/recent_tweet")
def send_recent_tweet_data():
    with Connection() as conn:
        cur = conn.cursor()
        livetweet_query1 = "select r.create_at, l.top_left_long, l.top_left_lat, l.bottom_right_long, l.bottom_right_lat, l.id, r.text, r.text " \
                           "from records r,locations l where r.id=l.id " \
                          "and r.create_at between (SELECT current_timestamp - interval '2 day') and current_timestamp"

        livetweet_query = "select it.create_at, it.top_left_long, it.top_left_lat, it.bottom_right_long, it.bottom_right_lat, it.id, it.text, i.image_url from " \
                          "(select r.create_at, l.top_left_long, l.top_left_lat, l.bottom_right_long, l.bottom_right_lat, l.id, r.text " \
                          "from records r,locations l where r.id=l.id and r.create_at between (SELECT current_timestamp - interval '6 month') and current_timestamp) AS it LEFT JOIN images i on i.id = it.id where i.image_url is not null"




        cur.execute(livetweet_query)
        resp = make_response(
            jsonify(
                [{"create_at": time.isoformat(), "long": long, "lat": lat, "id": id, "text": text, "image": image} for
                 time, long, lat, _, _, id, text, image in
                 cur.fetchall()]))
        cur.close()
    return resp
