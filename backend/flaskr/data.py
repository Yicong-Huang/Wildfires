from flaskr.db import get_db
from flask import Blueprint, make_response, jsonify, request as flask_request

bp = Blueprint('data', __name__, url_prefix='/data')


@bp.route("/temp", methods=['POST', 'GET'])
def send_temp_data():
    request_json = flask_request.get_json(force=True)
    north = request_json['northEast']['lat']
    east = request_json['northEast']['lon']
    south = request_json['southWest']['lat']
    west = request_json['southWest']['lon']
    tid = request_json['tid']
    interval = request_json['interval']

    query = "SELECT * from Polygon_Aggregator_noaa0p25(%s, %s, %s)"
    poly = 'polygon(({0} {1}, {0} {2}, {3} {2}, {3} {1}, {0} {1}))'.format(north, west, east, south)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, (poly, tid, interval))
    resp = make_response(
        jsonify(
            [{"lng": lon, "lat": lat, "temperature": temperature} for lat, lon, temperature, _ in cur.fetchall()]))
    cur.close()
    return resp