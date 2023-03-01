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
    parser.add('--reading_port', type=str, required=True, help='Chat port for reading messages')
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
    parser.add('--sending_port', type=str, required=True, help='Chat port for sending messages')
    parser.add('--message', type=str, help='A message to send to the chat')
    return parser


def create_registration_parser() -> configargparse.ArgParser:
    root_path = Path(__file__).parent.parent.resolve()

    parser = configargparse.ArgParser(
        default_config_files=[os.path.join(root_path, 'config.yml')],
    )
    parser.add('--config', type=str, is_config_file=True, help='Config file path')
    parser.add('--host', type=str, required=True, help='Chat host')
    parser.add('--sending_port', type=str, required=True, help='Chat port for user registration')
    return parser


def create_client_parser() -> configargparse.ArgParser:
    root_path = Path(__file__).parent.parent.resolve()

    parser = configargparse.ArgParser(
        default_config_files=[os.path.join(root_path, 'config.yml')],
    )
    parser.add('--config', type=str, is_config_file=True, help='Config file path')
    parser.add('--host', type=str, required=True, help='Chat host')
    parser.add('--sending-port', type=str, required=True, help='Chat port for sending messages')
    parser.add('--reading-port', type=str, required=True, help='Chat port for reading messages')
    parser.add(
        '--history',
        default=os.path.join(root_path, 'minechat.history'),
        help='The path to the correspondence history file. \
            Default value: /path_to_project_root/minechat.history',
    )
    return parser
