import json
import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_SOCKET"]

app = App(token=SLACK_BOT_TOKEN)

views = re.compile(r"button_.+")


@app.view("outage_modal")
def handle_view_events(ack, body, logger):
    ack()
    logger.info(body)
    from pprint import pprint

    pprint(body)

    # 'view - state - values' are predefined
    title = body["view"]["state"]["values"]["name"]["title"]["value"]
    print(f"Title: {title}")

    internal_check = body["view"]["state"]["values"]["internal_check"]["select_frame"][
        "selected_option"
    ]["value"]
    print(f"Type: {internal_check}")

    # information is the block, description is the input
    description = body["view"]["state"]["values"]["information"]["description"]["value"]
    print(f"Desc: {description}")

    print("Users:")
    for name in body["view"]["state"]["values"]["user_list"]["users"]["selected_users"]:
        print(name)

    date = body["view"]["state"]["values"]["date_picker"]["date"]["selected_date"]
    print(f"Date: {date}")


@app.event("app_mention")
def mention_handler(body, say):
    say("Awaiting an outage")


@app.action(views)
def handle_view_events(ack, body, logger):
    ack()
    logger.info(body)
    print("button pressed!")


@app.command("/outage")
def handle_some_command(ack, body, logger, client):
    ack()
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            # View identifier
            "callback_id": "outage_modal",
            "title": {"type": "plain_text", "text": "Outage"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please select the teams that are needed:",
                    },
                },
                {
                    "type": "actions",
                    "block_id": "button_block",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "R&D"},
                            "value": "rnd",
                            "action_id": "button_rnd",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Networking"},
                            "value": "net",
                            "action_id": "button_net",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Services"},
                            "value": "ops",
                            "action_id": "button_ops",
                        },
                    ],
                },
                {
                    "type": "section",
                    "block_id": "internal_check",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Is the issue internal or customer facing?",
                    },
                    "accessory": {
                        "action_id": "select_frame",
                        "type": "static_select",
                        "placeholder": {"type": "plain_text", "text": "Select an item"},
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Internal",
                                },
                                "value": "internal",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Customer Facing",
                                },
                                "value": "customer_facing",
                            },
                        ],
                    },
                },
                {
                    "type": "section",
                    "block_id": "user_list",
                    "text": {"type": "mrkdwn", "text": "Pick users from the list"},
                    "accessory": {
                        "action_id": "users",
                        "type": "multi_users_select",
                        "placeholder": {"type": "plain_text", "text": "Select users"},
                    },
                },
                {
                    "type": "section",
                    "block_id": "date_picker",
                    "text": {"type": "mrkdwn", "text": "When did the outage start"},
                    "accessory": {
                        "type": "datepicker",
                        "action_id": "date",
                        "initial_date": "2001-05-16",
                        "placeholder": {"type": "plain_text", "text": "Select a date"},
                    },
                },
                {
                    "type": "input",
                    "block_id": "name",
                    "label": {
                        "type": "plain_text",
                        "text": "Title",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title",
                        "multiline": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "information",
                    "label": {
                        "type": "plain_text",
                        "text": "Describe the Outage",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "description",
                        "multiline": True,
                    },
                },
            ],
        },
    )


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
