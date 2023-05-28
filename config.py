from json import loads;

with open("config.json") as config_file:
    config = loads(config_file.read());
