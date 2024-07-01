from highrise import BaseBot, Item

class ClothesManagerBot(BaseBot):
    def __init__(self, highrise):
        super().__init__()
        self.highrise = highrise

    async def get_inventory(self):
        inventory = await self.highrise.get_inventory()
        print(f"Fetched inventory: {inventory}")
        return inventory

    async def change_outfit(self, outfit):
        inventory = await self.get_inventory()
        inventory_item_ids = {item.id for item in inventory.items}

        for item in outfit:
            if item.id not in inventory_item_ids:
                print(f"Item {item.id} not found in inventory.")
                await self.highrise.chat(f"Failed to change outfit. Item {item.id} not found in inventory.")
                return

        await self.highrise.set_outfit(outfit=outfit)
        print(f"Outfit changed to: {outfit}")

    async def on_chat(self, user, message):
        if message.lower().startswith("/equip"):
            outfit = [
                Item(
                    type='clothing',
                    amount=1,
                    id='hair_front-n_malenew33',
                    account_bound=False,
                    active_palette=1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='hair_back-n_malenew33',
                    account_bound=False,
                    active_palette=1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='body-flesh',
                    account_bound=False,
                    active_palette=27
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='eye-n_basic2018malesquaresleepy',
                    account_bound=False,
                    active_palette=7
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='eyebrow-n_basic2018newbrows07',
                    account_bound=False,
                    active_palette=0
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='nose-n_basic2018newnose05',
                    account_bound=False,
                    active_palette=0
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='mouth-basic2018chippermouth',
                    account_bound=False,
                    active_palette=-1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='glasses-n_starteritems201roundframesbrown',
                    account_bound=False,
                    active_palette=-1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='bag-n_room32019sweaterwrapblack',
                    account_bound=False,
                    active_palette=-1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='shirt-n_starteritems2019tankwhite',
                    account_bound=False,
                    active_palette=-1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='shorts-f_pantyhoseshortsnavy',
                    account_bound=False,
                    active_palette=-1
                ),
                Item(
                    type='clothing',
                    amount=1,
                    id='shoes-n_whitedans',
                    account_bound=False,
                    active_palette=-1
                ),
            ]
            await self.change_outfit(outfit)
            await self.highrise.chat(f"{user.username}, I've changed my outfit!")
            print(f"{user.username} requested an outfit change.")
