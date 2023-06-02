from discord import Intents, Embed, Game, CustomActivity, ActivityType, PartialEmoji, Status;
from discord.client import Client;
from discord import Activity;
from discord import channel;
DMChannel = channel.DMChannel;

from nuthelper.logger import Logger;
from config import config;
import time;
from nuthelper.timehelper import getTimeFromMessage;

def formatMessageContent(content):
    return f"```\n{content.replace('```', '` ` `')}\n```";

# class MyActivity(Activity):
#     def __init__(self):
#         Activity.__init__(self);
#         self.name = "Hello1";
#         self.state = "Hello2";
#         self.type = ActivityType.custom;
#         self.details = "Hello3";
#         self.buttons = [
#             "Button1",
#             "Button2"
#         ];
class Presence():
    def __init__(self, status, activity):
        self.status = status;
        self.activity = activity;

class Presences:
    starting_up = Presence(Status.dnd, Game("Starting up..."))
    started = Presence(Status.online, Game("Check out my code! https://github.com/TechHog8984/Nut-Helper-Bot-V2"))

class NutHelper(Client):
    message_logs = {};

    def __init__(self, intents = Intents):
        Client.__init__(self, intents = intents);

    async def changePresence(self, presence):
        await self.change_presence(status = presence.status, activity = presence.activity);

    def fetchField1(self, field, value):
        if value == None:
            raise Exception("Failed to fetch " + field); # generic Exception because I don't care.
        setattr(self, field, value);
        print("Successfully fetched " + field);

    async def fetchField2(self, field, value):
        if value == None:
            raise Exception("Failed to fetch " + field); # generic Exception because I don't care.
        setattr(self, field, value);
        await self.logger.log(f"Successfully fetched **{field}**.");

    async def on_ready(self):
        await self.changePresence(Presences.starting_up);
        self.fetchField1("guild", self.get_guild(config.get("Guild ID")));
        self.fetchField1("bot_logs_channel", self.guild.get_channel(config.get("Bot Logs Channel ID")));
        self.fetchField1("avatar_url", self.user.display_avatar.url);

        self.base_embed = Embed();
        self.base_embed.set_footer(text = "Nut Helper | made by: TechHog#8984", icon_url = self.avatar_url);

        self.logger = Logger(self);
        await self.logger.init();

        await self.fetchField2("reaction_role_role", self.guild.get_role(config.get("ReactionRole Role ID")));
        await self.fetchField2("rules_channel", self.guild.get_channel(config.get("Rules Channel ID")));
        reaction_role_message = await self.rules_channel.fetch_message(config.get("ReactionRole Message ID"));
        await self.fetchField2("reaction_role_message", reaction_role_message);
        await self.fetchField2("message_logs_channel", self.guild.get_channel(config.get("Message Logs Channel ID")));

        self.message_logs_ignored_categories = [];
        ignored_category_ids = config.get("Message Logs Ignored Category IDs");
        for value in self.guild.by_category():
            category = value[0];
            if category != None and (category.id in ignored_category_ids):
                self.message_logs_ignored_categories.append(category);
                await self.logger.log(f"Added category '**{category.name}**' to message_logs_ignored_categories.");

        await self.logger.log("Bot successfully started!");
        await self.changePresence(Presences.started);

    async def on_member_join(self, member):
        # await self.bot_logs_channel.send(embed = self.base_embed.copy().)
        await self.logger.log(f"Member joined! - {member.name}#{member.discriminator} (<@{member.id}>)");
        await self.reaction_role_message.remove_reaction("☑️", member);
        await member.remove_roles(self.reaction_role_role, reason = "Joined server");

    async def on_member_remove(self, member):
        await self.logger.log(f"Member left! - {member.name}#{member.discriminator} (<@{member.id}>)");
        await self.reaction_role_message.remove_reaction("☑️", member);

    async def on_raw_reaction_add(self, payload):
        if payload.message_id != self.reaction_role_message.id:
            return;
        # remove all reactions that aren't the desired emoji
        if payload.emoji.name != "☑️":
            msg = await self.reaction_role_message.fetch(); #fetch so it has latest reactions
            for reaction in msg.reactions:
                emoji = reaction.emoji;
                emojiname = (type(emoji) == str and emoji) or emoji.name;

                if emojiname != "☑️":
                    await reaction.clear();
            return;

        await payload.member.add_roles(self.reaction_role_role, reason = "Reaction role");

    async def on_message(self, message):
        author = message.author;
        if author == self.user:
            return;
        channel = message.channel;
        if type(channel) != DMChannel:
            channel_category = channel.category;
            if channel_category == None or channel_category in self.message_logs_ignored_categories:
                return;

        content = message.content;
        guild = message.guild;

        await self.logMessage(message, author, channel, content, guild);
        await self.handleCommand(message, author, channel, guild, content);

    async def logMessage(self, message, author, channel, content, guild):
        embed = self.base_embed.copy();
        embed.title = "Message Logger";
        embed.url = f"https://discordapp.com/channels/{guild and guild.id or '@me'}/{channel.id}/{message.id}";
        embed.add_field(name = "User", value = f"<@{author.id}>");
        if guild:
            embed.add_field(name = "Channel", value = f"<#{channel.id}>");
        else:
            embed.add_field(name = "Channel", value = "*Direct Messages*");

        created_at = message.created_at;
        embed.add_field(name = "Created on", value = getTimeFromMessage(message));
        embed.add_field(name = "Content", value = formatMessageContent(content), inline = True);

        if len(message.attachments) > 0:
            value = "";
            for attachment in message.attachments:
                value += attachment.url + "\n";
            embed.add_field(name = "Attachments", value = value);

        if message.reference:
            reference = message.reference;
            reference_log = self.message_logs.get(reference.message_id);

            value = f"https://discordapp.com/channels/{guild.id}/{reference.channel_id}/{reference.message_id}";
            if reference_log:
                log = reference_log["log"];
                value = f"https://discordapp.com/channels/{guild.id}/{log.channel.id}/{log.id} ({value})";

            embed.add_field(name = "Reference", value = value);

        log = await self.message_logs_channel.send(embed = embed);
        self.message_logs[message.id] = {
            "message": message,
            "log": log,
            "last_content": content
        };

    async def sendFailEmbed(self, channel, message):
        embed = self.base_embed.copy()
        embed.description = "An error occured: " + message;
        await channel.send(embed = embed);

    async def handleCommand(self, message, author, channel, guild, content):
        if not content.startswith("!"):
            return;
        if author.id != 402264559509045258:
            return;

        content = content[1:];
        split = content.split(" ");
        if len(split) < 1:
            return;
        command = split[0];
        split.pop(0);

        if command == "purge":
            if len(split) < 1:
                return await self.sendFailEmbed(channel, "Purge expects an amount");

            amount = None;
            try:
                amount = int(split[0]);
            except:
                return await self.sendFailEmbed(channel, f"Failed to convert '`{split[0]}`' to an integer");

            await message.delete();
            await channel.purge(limit = amount);

    async def on_raw_message_edit(self, payload):
        message_id = payload.message_id;
        log = self.message_logs.get(message_id);
        if log == None:
            return;

        message = log["message"];
        content = message.content;
        if content == log["last_content"]:
            return;

        log["last_content"] = content;
        log_message = log["log"];
        embed = log_message.embeds[0];
        embed.set_field_at(3, name = "Content", value = embed.fields[3].value + " -> " + formatMessageContent(content), inline = True)
        if not log.get("edited"):
            embed.add_field(name = "Edited", value = "**True**");
            log["edited"] = True;
        await log_message.edit(embed = embed);

    async def on_raw_message_delete(self, payload):
        message_id = payload.message_id;
        log = self.message_logs.get(message_id);
        if log == None:
            return;

        log = log["log"];
        await log.edit(embed = log.embeds[0].
            add_field(name = "Deleted", value = "**True**")
        );
