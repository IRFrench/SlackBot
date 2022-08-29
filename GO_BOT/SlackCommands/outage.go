package SlackCommands

import (
	"fmt"
	"os"
	"time"

	"github.com/joho/godotenv"
	"github.com/slack-go/slack"
)

func SendMessage() {

	godotenv.Load(".env")

	token := os.Getenv("SLACK_TOKEN")
	channelID := os.Getenv("SLACK_CHANNEL_ID")

	client := slack.New(token, slack.OptionDebug(true))
	attachment := slack.Attachment{
		Pretext: "Slack Attachment",
		Text:    "This is an attachment",
		Color:   "4af030",
		Fields: []slack.AttachmentField{
			{
				Title: "Date:",
				Value: time.Now().String(),
			},
		},
	}

	_, timestamp, err := client.PostMessage(
		channelID,

		slack.MsgOptionAttachments(attachment),
	)

	if err != nil {
		panic(err)
	}
	fmt.Printf("Message sent at %s", timestamp)
}
