from concurrent.futures import Future
from pathlib import Path

import yaml
from endstone import ColorFormat
from endstone.event import PlayerJoinEvent, event_handler
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

from endstone_blackbe import blackbe_api


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
    def on_enable(self):
        self.register_events(self)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if len(args) != 1:
            return False

        def callback(status: Future[blackbe_api.BlackBeStatus]):
            if status.result() is None:
                sender.send_message(f"{ColorFormat.GREEN}Player isn't found in BlackBE database")
                return
            sender.send_message(f"{ColorFormat.YELLOW}Player is found in BlackBE database!")
            sender.send_message(status.result().__str__())

        match command.name:
            case "bq_name":
                blackbe_api.query_status_by_name(args[0].strip('"')).add_done_callback(callback)
            case "bq_qq":
                blackbe_api.query_status_by_qq(int(args[0])).add_done_callback(callback)

        return True

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        name = event.player.name

        def callback(status: Future[blackbe_api.BlackBeStatus]):
            if status.result() is not None:
                event.player.kick("You are recorded in BlackBE!")
                self.logger.info(f"{ColorFormat.RED}Player {name} failed BlackBE check!")
                self.logger.info(status.result().__str__())
            else:
                self.logger.info(f"{ColorFormat.GREEN}Player {name} passed BlackBE check!")

        blackbe_api.query_status_by_name(name).add_done_callback(callback)
