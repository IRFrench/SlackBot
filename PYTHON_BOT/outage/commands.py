from datetime import date
from dataclasses import dataclass
import typing as t

from slack_sdk.errors import SlackApiError


@dataclass
class outageInfo:
    title: str
    facing: str
    description: str
    users: t.List[str]
    start_date: date
    creator: str
    selected_teams: t.List[str]


def submit_outage(ack, body, logger, client):
    logger.info(body)

    teams = []
    for selected_team in body["view"]["state"]["values"]["team-selection"][
        "team-select"
    ]["selected_options"]:
        teams.append(selected_team["value"])

    current_outage = outageInfo(
        title=body["view"]["state"]["values"]["name"]["title"]["value"],
        facing=body["view"]["state"]["values"]["internal_check"]["select_frame"][
            "selected_option"
        ]["value"],
        description=body["view"]["state"]["values"]["information"]["description"][
            "value"
        ],
        users=body["view"]["state"]["values"]["user_list"]["users"]["selected_users"],
        start_date=date.fromisoformat(
            body["view"]["state"]["values"]["date_picker"]["date"]["selected_date"]
        ),
        creator=body["user"]["id"],
        selected_teams=teams,
    )

    # Create a channel for the outage
    try:
        channel_create_response = client.conversations_create(
            name=f"{date.isoformat(current_outage.start_date)}_{current_outage.title.replace(' ', '_').lower()}",
            is_private=False,
        )
    except SlackApiError as err:
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"Error: {err}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Could not create outage:* {err.response['error']}",
                    },
                },
            ],
        )
        ack()
        return

    channel = channel_create_response["channel"]["id"]
    bot = channel_create_response["channel"]["creator"]

    client.conversations_setTopic(channel=channel, topic=current_outage.title)

    client.conversations_setPurpose(channel=channel, purpose=current_outage.description)

    if current_outage.creator not in current_outage.users:
        current_outage.users.append(current_outage.creator)

    if bot in current_outage.users:
        current_outage.users.remove(bot)

    user_list = ",".join(current_outage.users)

    client.conversations_invite(channel=channel, users=user_list)

    message_response = client.chat_postMessage(
        channel=channel,
        text=current_outage.title,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"@here *{current_outage.title}*"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{current_outage.description}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Affecting:* {current_outage.facing}",
                },
            },
            {
                "type": "actions",
                "block_id": "close_outage",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "close_outage",
                        "text": {
                            "type": "plain_text",
                            "text": "Close Outage",
                        },
                        "style": "danger",
                        "value": channel,
                    }
                ],
            },
        ],
    )

    client.pins_add(channel=channel, timestamp=message_response["ts"])

    ack()


# Display a modal when using the /outage
# https://api.slack.com/surfaces/modals
# https://app.slack.com/block-kit-builder
def outage_slash_command(ack, body, logger, client):
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
                    "block_id": "team-selection",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Required teams:*",
                    },
                    "accessory": {
                        "type": "checkboxes",
                        "options": [
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "R&D",
                                },
                                "description": {
                                    "type": "mrkdwn",
                                    "text": "The R&D separtment",
                                },
                                "value": "rnd",
                            },
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Networking",
                                },
                                "description": {
                                    "type": "mrkdwn",
                                    "text": "The Networking department",
                                },
                                "value": "neteng",
                            },
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Services",
                                },
                                "description": {
                                    "type": "mrkdwn",
                                    "text": "The Services department",
                                },
                                "value": "services",
                            },
                        ],
                        "action_id": "team-select",
                    },
                },
                {
                    "type": "section",
                    "block_id": "internal_check",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Affecting:*",
                    },
                    "accessory": {
                        "action_id": "select_frame",
                        "type": "static_select",
                        "initial_option": {
                            "text": {
                                "type": "plain_text",
                                "text": "Internal Staff",
                            },
                            "value": "Internal",
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Internal Staff",
                                },
                                "value": "Internal",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Customer Facing",
                                },
                                "value": "Customers",
                            },
                        ],
                    },
                },
                {
                    "type": "section",
                    "block_id": "user_list",
                    "text": {"type": "mrkdwn", "text": "*Additional stakeholders:*"},
                    "accessory": {
                        "action_id": "users",
                        "type": "multi_users_select",
                        "placeholder": {"type": "plain_text", "text": "Select users"},
                    },
                },
                {
                    "type": "section",
                    "block_id": "date_picker",
                    "text": {"type": "mrkdwn", "text": "*Outage start:*"},
                    "accessory": {
                        "type": "datepicker",
                        "action_id": "date",
                        "initial_date": date.isoformat(date.today()),
                        "placeholder": {"type": "plain_text", "text": "Select a date"},
                    },
                },
                {
                    "type": "input",
                    "block_id": "name",
                    "label": {
                        "type": "plain_text",
                        "text": "Title:",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title",
                    },
                },
                {
                    "type": "input",
                    "block_id": "information",
                    "label": {
                        "type": "plain_text",
                        "text": "Outage Description:",
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


def close_outage(ack, body, logger, client):
    ack()
    logger.info(body)

    client.conversations_archive(channel=body["channel"]["id"])
