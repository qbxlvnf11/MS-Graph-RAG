import os
import requests
import subprocess
import asyncio
import datetime
import re
import argparse
from pathlib import Path

from rag_lib.config.load_config import load_config
from rag_lib.logger.print_progress import PrintProgressLogger
from rag_lib.config.enums import CacheType, IndexingMethod
from core.local_query import run_local_search

from utils import load_yaml

logger = PrintProgressLogger("")

def get_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--search_method', type=str, required=True, \
        choices=['local', 'global'])
    parser.add_argument('--query', type=str, required=True)
    parser.add_argument('--system_config_path', type=str, required=True)

    return parser.parse_args()

if __name__ == '__main__' :
    
    args = get_args()
    logger.info(f'Indexing start ...')

    system_config = load_yaml(args.system_config_path)
    project_root_folder = system_config['project_root_folder']

    logger.info(f'Project root folder: {project_root_folder}')

    # config = load_config(Path(project_root_folder))
    config_filepath = Path(os.path.join(project_root_folder, 'settings.yaml'))
    data_dir = Path('output')
    community_level = system_config['community_level']
    response_type = system_config['response_type']
    streaming = system_config['streaming']
    query = args.query
    
    if args.search_method == 'local':
        run_local_search(
            config_filepath=config_filepath,
            data_dir=data_dir,
            root_dir=Path(project_root_folder),
            community_level=community_level,
            response_type=response_type,
            streaming=streaming,
            query=query,
        )