import sys
from pathlib import Path

import str_templates
from classes import CommandNotExist
from commandtrie import TrieNode, build_command_trie
from helpers import shell_input
from settings import Settings


def config() -> Settings:
    settings = Settings.from_disk(Path("settings.json"))

    command_trie_root: TrieNode = build_command_trie(settings)
    command: TrieNode = command_trie_root
    while True:
        try:
            input = shell_input(settings.instance)
            command = command_trie_root
            args_starting_index: int = 0

            for command_part in input:
                if command_part not in command.subcommands:
                    break
                command = command.subcommands[command_part]
                args_starting_index += 1
            args = input[args_starting_index:] if len(input) > args_starting_index else []
                
            if command.fn is None:
                raise CommandNotExist(
                    str_templates.ERR_COMMAND_NONEXISTENT.format(" ".join(args))
                )

            for preprocessor_fn, preprocessor_args in zip(
                command.preprocessor_fn, command.preprocessor_args
            ):
                args = preprocessor_fn(args, *preprocessor_args)

            command.fn(*args)

            settings.write_to_json()

        except KeyboardInterrupt:
            settings.write_to_json()
            sys.exit(0)
        except (CommandNotExist, ValueError) as e:
            print(e)
        except TypeError as e:
            print(e)
            print(command.help)
    return settings
