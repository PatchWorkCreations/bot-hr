import os
import sys
from highrise import main as highrise_main
from bot import Bot
from clothes_manager import ClothesManagerBot

if __name__ == "__main__":
    os.environ["HIGHRISE_ROOM_ID"] = "6679c29a3d11ff193c6fcdc2"
    os.environ["HIGHRISE_API_TOKEN"] = "ba0b718b840c67702b7b681882dd8d1d44faf67dd53ae0e48f3dafdb879be715"

    room_id = os.getenv("HIGHRISE_ROOM_ID")
    api_token = os.getenv("HIGHRISE_API_TOKEN")

    if not room_id or not api_token:
        print("Room ID or API token not provided")
        sys.exit(1)

    bot = Bot()
    bot.clothes_manager = ClothesManagerBot(bot)
    highrise_main(bot)
