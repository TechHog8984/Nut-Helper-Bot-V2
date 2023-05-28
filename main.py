from nuthelper import NutHelper;
from discord import Intents;
from config import config;

intents = Intents.default();
intents.message_content = True;
intents.members = True;

NutHelper(intents = intents).run(config.get("token"));
