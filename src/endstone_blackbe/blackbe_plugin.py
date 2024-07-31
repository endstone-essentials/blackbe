from pathlib import Path

import yaml
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin


# NOTE(Vincent): maybe we can consider making this part of endstone api?
def plugin_metadata(filename):
    def decorator(cls):
        with (Path(__file__).parent / filename).open("r") as file:
            data = yaml.safe_load(file)
        for key, value in data.items():
            setattr(cls, key, value)
        return cls

    return decorator


@plugin_metadata("plugin.yml")
class BlackBePlugin(Plugin):
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        return True

