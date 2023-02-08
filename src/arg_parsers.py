import os
from pathlib import Path
import configargparse


def create_record_history_parser() -> configargparse.ArgParser:
    root_path = Path(__file__).parent.parent.resolve()

    parser = configargparse.ArgParser(
        default_config_files=[os.path.join(root_path, 'config.yml')],
    )
    parser.add('--config', type=str, is_config_file=True, help='Config file path')
    parser.add('--host', type=str, required=True, help='Chat host')
    parser.add('--port', type=str, required=True, help='Chat port')
    parser.add(
        '--history',
        default=os.path.join(root_path, 'minechat.history'),
        help='The path to the correspondence history file. \
            Default value: /path_to_project_root/minechat.history',
    )
    return parser


def create_sender_parser() -> configargparse.ArgParser:
    root_path = Path(__file__).parent.parent.resolve()

    parser = configargparse.ArgParser(
        default_config_files=[os.path.join(root_path, 'config.yml')],
    )
    parser.add('--config', type=str, is_config_file=True, help='Config file path')
    parser.add('--host', type=str, required=True, help='Chat host')
    parser.add('--port', type=str, required=True, help='Chat port')
    parser.add('--interactive', action='store_true', help='Enable interactive mode')
    parser.add('--message', type=str, required=True, help='A message to send to the chat')
    return parser


def create_registration_parser() -> configargparse.ArgParser:
    root_path = Path(__file__).parent.parent.resolve()

    parser = configargparse.ArgParser(
        default_config_files=[os.path.join(root_path, 'config.yml')],
    )
    parser.add('--config', type=str, is_config_file=True, help='Config file path')
    parser.add('--host', type=str, required=True, help='Chat host')
    parser.add('--port', type=str, required=True, help='Chat port')
    return parser