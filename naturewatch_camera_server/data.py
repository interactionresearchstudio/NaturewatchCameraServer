from flask import Blueprint, Response, request, json, send_from_directory
from flask import current_app
import time
import json
import os

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


@data.route('/download/<filename>')
def get_download(filename):
    file_path = current_app.user_config["videos_path"] + filename + '.mp4'
    if os.path.isfile(os.path.join(file_path)):
        output = current_app.file_saver.download_zip(filename + '.mp4')
        return send_from_directory(os.path.join('static/data/videos'), filename + ".mp4" + ".zip", mimetype="application/zip")
    else:
        return Response("{'NOT_FOUND':'" + filename + "'}", status=404, mimetype='application/json')


@data.route('/download/video')
def download_all():
    current_app.file_saver.download_all_video()
    return Response("{'NOT_FOUND':'" "'}", status=404, mimetype='application/json')


@data.route('/photos/<filename>', methods=["DELETE"])
def delete_photo(filename):
    file_path = current_app.user_config["photos_path"] + filename
    if os.path.isfile(os.path.join(file_path)):
        os.remove(file_path)
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
    if os.path.isfile(os.path.join(file_path)):
        os.remove(file_path)
        if os.path.isfile(os.path.join(file_path)) is False:
            return Response('{"SUCCESS": "' + filename + '"}', status=200, mimetype='application/json')
        else:
            return Response('{"ERROR": "' + filename + '"}', status=500, mimetype='application/json')


def construct_directory_list(current_app, path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if f.lower().endswith(('.jpg', '.mp4'))]
    files = [f for f in files if not f.lower().startswith('thumb_')]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(get_correct_filepath(current_app,f))), reverse=True)
    return files

def get_correct_filepath(current_app, path):
    if path.lower().endswith('.jpg'):
        return os.path.join(current_app.user_config["photos_path"], path)
    elif path.lower().endswith('.mp4'):
        return os.path.join(current_app.user_config["videos_path"], path)
