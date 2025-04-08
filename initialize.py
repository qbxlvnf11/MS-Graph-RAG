import argparse

from utils import load_yaml

from rag_lib.logger.print_progress import PrintProgressLogger
from core.initialize_project import initialize_custom_project

logger = PrintProgressLogger("")

def get_args():
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--system_config_path', type=str, required=True)

    return parser.parse_args()

if __name__ == '__main__' :
    
    args = get_args()

    system_config = load_yaml(args.system_config_path)
    project_root_folder = system_config['project_root_folder']

    logger.info(f'Project root folder: {project_root_folder}')

    initialize_custom_project(project_root_folder, force=False)
