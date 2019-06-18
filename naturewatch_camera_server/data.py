from flask import Blueprint, Response, request, json
from flask import current_app
import time
import json
import os

data = Blueprint('data', __name__)


@data.route('/photos', methods=["GET", "DELETE"])
def photos_request_handler():
    if request.method == "GET":
        photos_list = construct_directory_list(current_app.user_config["photos_path"])
        return Response(json.dumps(photos_list), mimetype='application/json')


def construct_directory_list(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files
