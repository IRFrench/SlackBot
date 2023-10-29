def mention_handler(body, say):
    say("Awaiting an outage")


def ignore(ack, body, logger):
    ack()
    logger.info(body)
