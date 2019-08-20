from flask import Blueprint, Response, send_from_directory, current_app
import os

static_page = Blueprint('static_page', __name__)


@static_page.route('/', defaults={'path': ''})
@static_page.route('/<path:path>')
def serve(path):
    """
    Static root endpoint
    :return: index.html or file requested
    """
    if path != "" and os.path.exists(os.path.join(current_app.static_folder, path)):
        return send_from_directory(current_app.static_folder, path)
    elif path == "" or "gallery" in path:
        return send_from_directory(current_app.static_folder, 'index.html')
    else:
        return Response("Page not found. Please check the URL!", status=404)
