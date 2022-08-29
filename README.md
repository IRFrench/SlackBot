# Awesome Bot

Why is every bot not called awesome bot? It implies that the bot is awesome. Great for marketing. "Have you seen the new awesome bot? Its awesome".

## Go bot

The Golang slack intergrations are more complex when it comes to development for me. This is because I am new to the language and slack intergration, making it hard knowing if I am on the right path.

For now, the Python bot will be better and I will return to Go after learning more about creating a slack application

## Python bot

Uses `slack-bolt` for the application.

Simply, the client connects to a socket and binds to the Slack workspace. This allows the slash commands to be picked up instantly without relying on http servers.

The way the bot works currently is for a single slash function, acting as a prototype system that would work for outages. This system would record data from the user and can then send this around. So far it can create the modal to enter the data and display this back in the terminal. Later on, this system will create a slack channel for the outage, add the selected users and write a summery in the channel. This will also throw a short announcement in another channel, acting like a general channel to let everyone know there is an issue.

Other intergrations will be needed for the full idea, but that is out of the scope for this project.