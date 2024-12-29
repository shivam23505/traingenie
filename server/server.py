#!/usr/bin/env python3

import json

from flask import Flask, request, jsonify, render_template
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--train_db", help="train database JSON",
                    type=str, required=True)
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='static/html')

train_data = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/train_info', methods=['GET'])
def get_train_info_html():
    train_number = request.args.get('train_number')
    if train_number in train_data:
        return render_template('train_info.html', train=train_data.get(train_number, {}))
    else:
        return "Train not found : " + str(train_number), 404
    
@app.route('/api/v1/train_info', methods=['GET'])
def get_train_info_api():
    train_number = request.args.get('train_number')
    if train_number in train_data:
        return jsonify(train_data[train_number])
    return jsonify({}), 404


def train_predicate(train: dict, start_station: str = None,
                    end_station: str = None, day_of_week: str = None):
    return (not start_station or start_station == train['source']) \
        and (not end_station or end_station == train['dest']) \
        and (not day_of_week or day_of_week in train['days'])


def train_search_algo(*args, **kwargs):
    filtered_data = filter(lambda train: train_predicate(train, *args, **kwargs), train_data.values())
    return list(filtered_data)

@app.route('/train_search', methods=['GET'])
def train_search_html():
    start_station = request.args.get('start_station', None)
    end_station = request.args.get('end_station', None)
    return render_template('trains.html', trains=train_search_algo(start_station=start_station, end_station=end_station))


@app.route('/api/v1/train_search', methods=['GET'])
def train_search_api():
    start_station = request.args.get('start_station', None)
    end_station = request.args.get('end_station', None)
    return jsonify(train_search_algo(start_station=start_station, end_station=end_station))

if __name__ == '__main__':
    args = parser.parse_args()

    with open(args.train_db) as f:
        train_data = json.load(f)

    app.run(debug=True)
