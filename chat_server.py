import os
import requests
import subprocess
import asyncio
import datetime
import re
import argparse
import uvicorn
from pathlib import Path
import json

# from flask import Flask, request, Response, stream_with_context, jsonify, json, send_from_directory
# from flask_cors import CORS
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio

from system_scripts.test_system_script import (
   TEST_SYSTEM_PROMPT
)

from utils import load_yaml, get_folder, convert_context_json
from core.local_query import run_local_search
from core.global_query import run_global_search
from rag_lib.logger.print_progress import PrintProgressLogger

logger = PrintProgressLogger("")

# app = Flask(__name__)
app = FastAPI()

## CORS 설정
# CORS(app, resources={r"/*": {"origins": "*"}})
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# async def consume_async_data(stream):
#     async for data in stream(): 
#         # print(f"Consumed: {data}")
#         yield f"{data}"

async def run_streaming_search(stream, search_method):
    # for i in range(5):
    #     yield f"data: Chunk {i}\n\n"
    #     await asyncio.sleep(1)
    # yield f"{response}"

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # async_gen = consume_async_data(stream)

    # try:
    #     while True:
    #         data = loop.run_until_complete(async_gen.__anext__())
    #         yield (data).encode('utf-8')
    # except StopAsyncIteration:
    #     pass
    # finally:
    #     loop.close()

    result = await stream

    response = result[0]

    ## Response
    # yield response.encode("utf-8")
    # yield (response + "\n---RESPONSE-END---\n").encode("utf-8")
    yield json.dumps({
        "type": "response",
        "data": response
    }).encode("utf-8")
    
    if search_method == 'local':

        sources = result[1]['sources']
        entities = result[1]['entities']
        relationships = result[1]['relationships']
        reports = result[1]['reports']

        ## Sources
        # for index, row in sources.iterrows():
        #     sources_str = ''
        #     sources_str = f'== Source {index} ==\n'
        #     for column in sources.columns:
        #         sources_str += f"{column}: {row[column]} \n"
        #     yield f"{sources_str}".encode("utf-8")

        sources_context_list = convert_context_json(sources, "sources")
        for context in sources_context_list:
            yield context.encode("utf-8")

        ## Entities
        entities_context_list = convert_context_json(entities, "entities")
        for context in entities_context_list:
            yield context.encode("utf-8")

        ## Relationships
        relationships_context_list = convert_context_json(relationships, "relationships")
        for context in relationships_context_list:
            yield context.encode("utf-8")

        ## Reports
        reports_context_list = convert_context_json(reports, "reports")
        for context in reports_context_list:
            yield context.encode("utf-8")

    elif search_method == 'global':
        ## Response
        yield response.encode("utf-8")
    # yield ""
    # yield result[0].encode("utf-8")

def get_args():
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--server_port', type=int, default=8877)
    parser.add_argument('--rag_root_folder', type=str, default='rag_db')
    # parser.add_argument('--system_config_path', type=str, required=True)

    return parser.parse_args()

# @app.route('/main', methods=['POST', 'OPTIONS'])
# def test():

#     if request.method == 'OPTIONS':
#         response = jsonify({'message': 'CORS Passed'})
        
#         return response, 200

@app.post("/api")
async def test(request: Request):
    try:
        req_json = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)

    # system_config = load_yaml(request.app.state.system_config_path)
    # project_root_folder = system_config['project_root_folder']

    try:
        response = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)
    
    logger.info(response)
    
    query = response["query"]
    language = response["language"]
    llm_version = response["llm_version"]
    rag_version = response["rag_version"]
    search_method = response["search_method"]
    response_type = response["response_type"]
    community_level = 2
    if 'community_level' in response:
        community_level = response['community_level']
    dynamic_community_selection = False
    if 'dynamic_community_selection' in response:
        dynamic_community_selection = response['dynamic_community_selection']

    rag_root_folder = request.app.state.rag_root_folder
    rag_folder = get_folder(rag_version)
    project_root_folder = os.path.join(rag_root_folder, rag_folder)
    config_filepath = Path(os.path.join(rag_root_folder, rag_folder, 'settings.yaml'))
    data_dir = Path('output')
    web_streaming = True
    streaming = True

    logger.info(f'Project root folder: {project_root_folder}')
    logger.info(f'Config path: {config_filepath}')

    if search_method == 'local':
        stream = await run_local_search(
            config_filepath=config_filepath,
            data_dir=data_dir,
            root_dir=Path(project_root_folder),
            community_level=community_level,
            response_type=response_type,
            streaming=streaming,
            web_streaming=web_streaming,
            query=query,
        )
    elif search_method == 'global':
        stream = await run_global_search(
            config_filepath=config_filepath,
            data_dir=data_dir,
            root_dir=Path(project_root_folder),
            community_level=community_level,
            dynamic_community_selection=dynamic_community_selection,
            response_type=response_type,
            streaming=streaming,
            web_streaming=web_streaming,
            query=query,
        )
    else:
        return JSONResponse(content={"error": "Invalid search_method"}, status_code=400)

    # return JSONResponse(content={"response": response})
    return StreamingResponse(run_streaming_search(stream=stream, search_method=search_method), media_type="text/plain")

if __name__ == '__main__' :
    
    args = get_args()

    # app.run(
    #     ssl_context=None, #('cert.pem', 'key.pem'), #None
    #     host="0.0.0.0",
    #     port=args.port,
    #     debug=False)

    # app.state.system_config_path = args.system_config_path
    app.state.rag_root_folder = args.rag_root_folder

    uvicorn.run(
        app, #"chat_server:app",
        host="0.0.0.0",
        port=args.server_port,
        reload=False,
        ssl_certfile=None,  
        ssl_keyfile=None
    )
