from flask import Blueprint, send_from_directory
import os

static_page = Blueprint('static_page', __name__, static_folder='static')


@static_page.route('/', defaults={'path': ''})
@static_page.route('/<path:path>')
def serve(path):
    """
    Static root endpoint
    :return: index.html or file requested
    """
    if path != "" and os.path.exists('static' + path):
        return send_from_directory('static', path)
    else:
        return send_from_directory('static', 'index.html')
