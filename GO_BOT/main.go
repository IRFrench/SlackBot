package main

import (
	"fmt"
	"net/http"
	"os"
	"slackbot/SlackCommands"

	"github.com/joho/godotenv"
	"github.com/slack-go/slack"
	"github.com/slack-go/slack/socketmode"
)

func Outage(w http.ResponseWriter, req *http.Request) {

	// Send a message to the channel
	SlackCommands.SendMessage()
}

func main() {

	godotenv.Load(".env")

	token := os.Getenv("SLACK_TOKEN")
	// channelID := os.Getenv("SLACK_CHANNEL_ID")
	socket := os.Getenv("SLACK_SOCKET")

	client := slack.New(token, slack.OptionDebug(true), slack.OptionAppLevelToken(socket))

	api := socketmode.New(client)

	go func() {
		for evt := range api.Events {
			switch evt.Type {

			case socketmode.EventTypeConnecting:
				fmt.Println("Connecting to Slack with Socket Mode...")
			case socketmode.EventTypeConnectionError:
				fmt.Println("Connection failed. Retrying later...")
			case socketmode.EventTypeConnected:
				fmt.Println("Connected to Slack with Socket Mode.")

			case socketmode.EventTypeInteractive:
				callback, ok := evt.Data.(slack.InteractionCallback)
				if !ok {
					fmt.Printf("Ignored %+v\n", evt)

					continue
				}

				fmt.Println(callback)
				fmt.Println(evt)
				fmt.Println(ok)
				fmt.Println(evt.Request)
				fmt.Println(evt.Data)

				var payload interface{}

				api.Ack(*evt.Request, payload)

			case socketmode.EventTypeSlashCommand:
				cmd, ok := evt.Data.(slack.SlashCommand)
				if !ok {
					fmt.Printf("Ignored %+v\n", evt)

					continue
				}

				api.Debugf("Slash command received: %+v", cmd)

				payload := map[string]interface{}{
					"blocks": []slack.Block{
						slack.NewSectionBlock(
							&slack.TextBlockObject{
								Type: slack.MarkdownType,
								Text: "foo",
							},
							nil,
							slack.NewAccessory(
								slack.NewButtonBlockElement(
									"123",
									"somevalue",
									&slack.TextBlockObject{
										Type: slack.PlainTextType,
										Text: "bar",
									},
								),
							),
						),
						slack.NewSectionBlock(
							&slack.TextBlockObject{
								Type: slack.MarkdownType,
								Text: "Who is envolved?",
							},
							nil,
							slack.NewAccessory(
								slack.NewButtonBlockElement(
									"R&D",
									"R&D",
									&slack.TextBlockObject{
										Type: slack.PlainTextType,
										Text: "R&D",
									},
								),
							),
						),
					}}

				api.Ack(*evt.Request, payload)
			}
		}
	}()

	api.Run()

}

func RestServer() {

	http.HandleFunc("/Bot", Outage)

	http.ListenAndServe(":8090", nil)
}
