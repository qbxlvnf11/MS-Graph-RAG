import logging
import yaml
import os 

from rag_lib.logger.base import ProgressLogger

log = logging.getLogger(__name__)

def _logger(logger: ProgressLogger):
    def info(msg: str, verbose: bool = False):
        log.info(msg)
        if verbose:
            logger.info(msg)

    def error(msg: str, verbose: bool = False):
        log.error(msg)
        if verbose:
            logger.error(msg)

    def success(msg: str, verbose: bool = False):
        log.info(msg)
        if verbose:
            logger.success(msg)

    return info, error, success

def get_root_folder(rag_version):

    root_folder = None

    if rag_version == 1.0:
        root_folder = 'test'
    else:
        raise ValueError("Not exist rag version!")

    return root_folder

def load_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.safe_load(file)
            return yaml_data
    except FileNotFoundError:
        print(f"Error: file not found - {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error: parssing - {e}")
        return None
    
    