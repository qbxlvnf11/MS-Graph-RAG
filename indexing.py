import os
import datetime
import logging
import argparse
from pathlib import Path
import numpy as np
import asyncio

from rag_lib.config.load_config import load_config
from rag_lib.logger.print_progress import PrintProgressLogger
from rag_lib.config.enums import CacheType, IndexingMethod
from core.rag_indexing import indexing

from utils import load_yaml, _logger

# warnings.filterwarnings("ignore", message=".*NumbaDeprecationWarning.*")

logger = PrintProgressLogger("")

def get_args():
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--system_config_path', type=str, required=True)
    parser.add_argument('--fast', action='store_true')
    return parser.parse_args()

if __name__ == '__main__' :
    
    args = get_args()
    logger.info(f'Indexing start ...')

    system_config = load_yaml(args.system_config_path)
    project_root_folder = system_config['project_root_folder']

    logger.info(f'Project root folder: {project_root_folder}')

    output_dir = 'output' #os.path.join(project_root_folder, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    cli_overrides = {}
    if output_dir:
        cli_overrides["output.base_dir"] = str(output_dir)
        cli_overrides["reporting.base_dir"] = str(output_dir)
        cli_overrides["update_index_output.base_dir"] = str(output_dir)

    # config = load_config(Path(project_root_folder))
    config = load_config(Path(project_root_folder), \
        Path(os.path.join(project_root_folder, 'settings.yaml')), cli_overrides)

    method = IndexingMethod.Standard
    if args.fast:
        method = IndexingMethod.Fast
        
    # asyncio.run(indexing(config))
    indexing(config=config,
            method=method, 
            is_update_run=False,
            verbose=True,
            memprofile=False,
            cache=True,
            logger=logger,
            dry_run=False,
            skip_validation=False
        )