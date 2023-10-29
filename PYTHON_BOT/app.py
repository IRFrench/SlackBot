import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from outage.commands import (
    submit_outage,
    outage_slash_command,
    close_outage,
)
from general.response import mention_handler, ignore

from dataclasses import dataclass


@dataclass
class config:
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str


def add_general_commads(app: App):
    app.event("app_mention")(mention_handler)


def add_outage_commands(app: App):
    app.view_submission("outage_modal")(submit_outage)
    app.command("/outage")(outage_slash_command)
    app.action("close_outage")(close_outage)

    app.action("users")(ignore)
    app.action("select_frame")(ignore)
    app.action("team-select")(ignore)
    app.action("date")(ignore)


def run():
    if os.environ.get("DEV"):
        load_dotenv()

    configuration = config(
        SLACK_BOT_TOKEN=os.environ["SLACK_TOKEN"],
        SLACK_APP_TOKEN=os.environ["SLACK_SOCKET"],
    )

    app = App(token=configuration.SLACK_BOT_TOKEN)
    add_outage_commands(app)
    add_general_commads(app)

    handler = SocketModeHandler(app, configuration.SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    run()
