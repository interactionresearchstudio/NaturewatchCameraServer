from flask import Blueprint, Response, request, json, send_from_directory
from flask import current_app
import time
import json
import os

data = Blueprint('data', __name__)


@data.route('/photos')
def get_photos():
    photos_list = construct_directory_list(current_app.user_config["photos_path"])
    return Response(json.dumps(photos_list), mimetype='application/json')


@data.route('/photos/<filename>')
def get_photo(filename):
    file_path = current_app.user_config["photos_path"] + filename
    if os.path.isfile(os.path.join(file_path)):
        return send_from_directory(os.path.join('static/data/photos'), filename, mimetype="image/jpg")
    else:
        return Response("{'NOT_FOUND':'" + filename + "'}", status=404, mimetype='application/json')


@data.route('/photos/<filename>', methods=["DELETE"])
def delete_photo(filename):
    file_path = current_app.user_config["photos_path"] + filename
    if os.path.isfile(os.path.join(file_path)):
        os.remove(file_path)
        if os.path.isfile(os.path.join(file_path)) is False:
            return Response('{"SUCCESS": "' + filename + '"}', status=200, mimetype='application/json')
        else:
            return Response('{"ERROR": "' + filename + '"}', status=500, mimetype='application/json')


def construct_directory_list(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files
