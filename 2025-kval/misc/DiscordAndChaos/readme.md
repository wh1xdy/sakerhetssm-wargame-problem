# Setting up the server for this chall

## Channels

### #user
- Default public channel permissions (No overrides)
- Contains a message with big text saying "You are allowed to hack this discord server, as it is a part of a SSM chall"
- The channel description is "The Discord And Chaos chall from SSM"
- The invite leads to this channel

### #root
- Default private channl permissions (@everyone - View channel - Override to no)
- Messages in it are not important, as the solvers will never see them
- The channel description contains the flag

## SSM-Bot
- Not neccesary
- Has a hacker profile picture
- User description/bio is "There is nothing special about this bot, it just happens to be here! Look closer about what else is hidden around the server!" to let solvers know that this bot is not a important part of the chall
- Lets the server not be connected (owned) by a user, which means the creator can then leave the server
- Does not have a actual discord bot "in" it, but is controlled by http requests

## Server Settings
- Name: Currently "SSM-server", but that is not critical because the channel already contains info that this is a part of a SSM chall, so the name can be anything
- Server icon shoud be a image of a real server room **Very Important!**
- All extra functionality from the server settings disabled
- No: Emoji, Soundboard, Stickers, Bots needed, but in case you really want them they do not disturb either
- Not a community server
- Best way to create it is through the API with a bot user because that defaults all settings to null instead of the normal discord default value

### Roles
- No roles exept @everyone
- @everyone permissions: View channels, Read message history. *No other ones are needed*.

#### Notice: This is instructions for the hosters and chall creators on how to setup the discord server, they not intended to be seen by solvers
