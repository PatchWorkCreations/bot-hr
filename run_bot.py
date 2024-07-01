from highrise.__main__ import *
import time
from importlib import import_module

bot_file_name = "bot"
bot_class_name = "Bot"
room_id = "6679c29a3d11ff193c6fcdc2"
bot_token = "ba0b718b840c67702b7b681882dd8d1d44faf67dd53ae0e48f3dafdb879be715"

my_bot = BotDefinition(getattr(import_module(bot_file_name), bot_class_name)(), room_id, bot_token)

while True:
    try:
        definitions = [my_bot]
        arun(main(definitions))
    except Exception as e:
        print(f"An exception occurred: {e}")
        time.sleep(5)  # Wait for 5 seconds before restarting
