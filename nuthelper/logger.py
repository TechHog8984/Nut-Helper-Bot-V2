from nuthelper.timehelper import timeNow;

class Logger():
    def __init__(self, nuthelper):
        self.base_embed = nuthelper.base_embed;
        self.bot_logs_channel = nuthelper.bot_logs_channel;

    async def init(self):
        self.embed = self.base_embed.copy();
        self.embed.title = "Logs have been initiated on " + timeNow();
        self.embed.description = "";

        self.message = await self.bot_logs_channel.send(embed = self.embed);

    async def log(self, additional_content):
        self.embed.description += "\n" + additional_content;
        await self.message.edit(embed = self.embed);

        print(additional_content.replace("**", "")); # funny hack to get rid of bold astericks
