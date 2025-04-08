import os
import requests
import subprocess
import asyncio
import datetime
import re
import argparse

from flask import Flask, request, Response, stream_with_context, jsonify, json, send_from_directory
from flask_cors import CORS

from rag_lib.query import cli
from test_scripts import (
    test_system_script
)

from utils import get_root_foler

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_args():
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--port', type=int, default=8977)
    parser.add_argument('--system_config_path', type=str, required=True)

    return parser.parse_args()

@app.route('/main', methods=['POST', 'OPTIONS'])
def test():

    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS Preflight Passed'})
        
        return response, 200

    response = request.json
    user_input = request.get("input")
    language = request.json.get("language")
    llm_version = request.json.get("llm_version")
    rag_version = request.json.get("rag_version")
    search_method = request.get("search_method")
    response_type = request.get("response_type")

    root_folder = get_root_foler(rag_version)
    get__ = get_root_foler(llm_version)

    rag_config = f'{root_folder}/settings.yaml'
    system_config = f'{root_folder}/settings.yaml'

if __name__ == '__main__' :
    
    args = get_args()

    app.run(
        ssl_context=None, #('cert.pem', 'key.pem'), #None
        host="0.0.0.0",
        port=args.port,
        debug=False)
    