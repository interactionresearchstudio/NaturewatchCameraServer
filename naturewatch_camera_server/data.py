from flask import Blueprint, Response, request, json, send_from_directory
from flask import current_app
import json
import os

from .ZipfileGenerator import ZipfileGenerator

data = Blueprint('data', __name__)


@data.route('/photos')
def get_photos():
    photos_list = construct_directory_list(current_app, current_app.user_config["photos_path"])
    return Response(json.dumps(photos_list), mimetype='application/json')


@data.route('/videos')
def get_videos():
    videos_list = construct_directory_list(current_app, current_app.user_config["videos_path"])
    return Response(json.dumps(videos_list), mimetype='application/json')


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
    thumb_path = current_app.user_config["photos_path"] + "thumb_" + filename
    if os.path.isfile(os.path.join(file_path)):
        os.remove(file_path)
        os.remove(thumb_path)
        if os.path.isfile(os.path.join(file_path)) is False:
            return Response('{"SUCCESS": "' + filename + '"}', status=200, mimetype='application/json')
        else:
            return Response('{"ERROR": "' + filename + '"}', status=500, mimetype='application/json')


@data.route('/videos/<filename>')
def get_video(filename):
    file_path = current_app.user_config["videos_path"] + filename
    if os.path.isfile(os.path.join(file_path)):
        if filename.endswith(".jpg"):
            return send_from_directory(os.path.join('static/data/videos'), filename, mimetype="image/jpg")
        else:
            return send_from_directory(os.path.join('static/data/videos'), filename, mimetype="video/mp4")
    else:
        return Response("{'NOT_FOUND':'" + filename + "'}", status=404, mimetype='application/json')


@data.route('/videos/<filename>', methods=["DELETE"])
def delete_video(filename):
    file_path = current_app.user_config["videos_path"] + filename
    thumb_path = current_app.user_config["videos_path"] + "thumb_" + filename
    thumb_path = thumb_path.replace(".mp4", ".jpg")
    if os.path.isfile(os.path.join(file_path)):
        os.remove(file_path)
        os.remove(thumb_path)
        if os.path.isfile(os.path.join(file_path)) is False:
            return Response('{"SUCCESS": "' + filename + '"}', status=200, mimetype='application/json')
        else:
            return Response('{"ERROR": "' + filename + '"}', status=500, mimetype='application/json')


def get_all_files(app, src_path):
    # just for now... we should take an array of file names
    src_list = construct_directory_list(app, src_path)
    paths = list(map(lambda fn: {'filename': os.path.join(src_path, fn), 'arcname': fn}, src_list))
    return paths


@data.route('/download/videos.zip', methods=["POST", "GET"])
def download_videos():
    videos_path = current_app.user_config["videos_path"]
    if request.is_json:
        body = request.get_json()
        paths = list(map(lambda fn: {'filename': os.path.join(videos_path, fn), 'arcname': fn}, body["paths"]))
    else:
        paths = get_all_files(current_app, videos_path)
    return Response(ZipfileGenerator(paths).get(), mimetype='application/zip')


@data.route('/download/photos.zip', methods=["POST", "GET"])
def download_photos():
    photos_path = current_app.user_config["photos_path"]
    if request.is_json:
        body = request.get_json()
        paths = list(map(lambda fn: {'filename': os.path.join(photos_path, fn), 'arcname': fn}, body["paths"]))
    else:
        paths = get_all_files(current_app, photos_path)
    return Response(ZipfileGenerator(paths).get(), mimetype='application/zip')


def construct_directory_list(app, path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if f.lower().endswith(('.jpg', '.mp4'))]
    files = [f for f in files if not f.lower().startswith('thumb_')]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(get_correct_filepath(app, f))), reverse=True)
    return files


def get_correct_filepath(app, path):
    if path.lower().endswith('.jpg'):
        return os.path.join(app.user_config["photos_path"], path)
    elif path.lower().endswith('.mp4'):
        return os.path.join(app.user_config["videos_path"], path)
