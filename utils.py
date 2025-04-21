import logging
import yaml
import os 
import json 

from rag_lib.logger.base import ProgressLogger

log = logging.getLogger(__name__)

from rag_lib.logger.print_progress import PrintProgressLogger

print_logger = PrintProgressLogger("")

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

def get_folder(rag_version):

    root_folder = None

    print_logger.info(f'Rag version: {rag_version}')

    if rag_version == 'test_version':
        root_folder = 'test_version'
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
    
def convert_context_json(df, type):

    context_list = []
    for index, row in df.iterrows():
        # row_data = {col: row[col] for col in df.columns}
        context_str = ''
        context_str = f'======== {type} {index} ========\n'
        for column in df.columns:
            context_str += f"==== {column} ==== \n"
            context_str += f"{row[column]} \n\n"

        context_list.append(json.dumps({
            "type": type,
            "index": index,
            "data": context_str
        }))

    return context_list