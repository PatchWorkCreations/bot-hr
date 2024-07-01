from highrise import BaseBot, User, Position, CurrencyItem, Item
import random
from clothes_manager import ClothesManagerBot

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.clothes_manager = ClothesManagerBot(self)
        self.games = {}
        self.balances = {}
        self.bets = {}

    async def on_start(self, session_metadata):
        print("Hi, I'm alive!")

    async def whisper(self, user: User, message: str):
        await self.highrise.send_whisper(user.id, message)
        print(f"Whispered to {user.username}: {message}")

    async def on_chat(self, user: User, message: str) -> None:
        username = user.username
        message = message.lower()

        # Intentionally crash the bot randomly for testing
         # Increase the probability to 50% for testing purposes
        if random.random() < 1.00:  # 50% chance to crash
            raise Exception("Intentional crash for testing reconnection")

        if message.startswith("bet"):
            try:
                bet_amount = int(message.split()[1])
                await self.start_game(user, bet_amount)
            except (IndexError, ValueError):
                await self.highrise.chat(f"{username}, please specify a valid bet amount to start the game. Example: 'bet 10'")
        elif message == "hit":
            await self.hit(user)
        elif message == "stand":
            await self.stand(user)
        elif message == "cash out":
            await self.cash_out(user)
        elif message.startswith("cash out"):
            try:
                cashout_amount = int(message.split()[2])
                await self.cash_out(user, cashout_amount)
            except (IndexError, ValueError):
                await self.highrise.chat(f"{username}, please specify a valid cash out amount. Example: 'cash out 10'")
        elif message.startswith("bet again"):
            try:
                bet_amount = int(message.split()[2])
                await self.bet_again(user, bet_amount)
            except (IndexError, ValueError):
                await self.highrise.chat(f"{username}, please specify a valid bet amount to bet again. Example: 'bet again 10'")
        elif message == "wallet":
            await self.check_wallet()
        elif message == "gold":
            await self.check_gold()
        elif message == "balance":
            await self.check_balance(username)
        else:
            await self.highrise.chat(f"Sorry, I don't understand that, {username}.")

    async def start_game(self, user, bet_amount):
        username = user.username
        print(f"Starting game for {username} with bet amount {bet_amount}")
        print(f"Balances: {self.balances}")  # Debug print to check all balance records

        if username in self.balances:
            current_balance = self.balances[username].amount
            print(f"{username}'s current balance: {current_balance}")

            if current_balance >= bet_amount:
                self.bets[username] = bet_amount
                self.games[username] = {"player_hand": [], "dealer_hand": []}
                self.balances[username].amount -= bet_amount  # Deduct bet amount
                print(f"{username}'s balance after betting: {self.balances[username].amount}")
                await self.deal_initial_cards(user)
                await self.highrise.chat(f"Game started for {username} with a bet of {bet_amount} gold bars. Type 'hit' to draw a card or 'stand' to hold.")
                await self.highrise.chat(f"{username}, your balance is {self.balances[username].amount} gold bars.")
            else:
                print(f"{username} tried to start game with insufficient balance. Current balance: {current_balance}")
                await self.highrise.chat(f"{username}, you need to tip the bot to play the game or your bet amount is more than your balance. Your current balance is {current_balance} gold bars.")
        else:
            print(f"{username} does not have a balance record.")
            await self.highrise.chat(f"{username}, you need to tip the bot to play the game. You currently have no balance.")

    async def deal_initial_cards(self, user):
        username = user.username
        for _ in range(2):
            self.games[username]["player_hand"].append(self.draw_card())
            self.games[username]["dealer_hand"].append(self.draw_card())
        await self.show_hands(user, show_dealer=False)

    async def hit(self, user):
        username = user.username
        if username in self.games:
            self.games[username]["player_hand"].append(self.draw_card())
            await self.show_hands(user, show_dealer=False)
            if self.calculate_hand(self.games[username]["player_hand"]) > 21:
                await self.highrise.chat(f"{username}, you busted!")
                del self.games[username]
                del self.bets[username]
        else:
            await self.highrise.chat(f"No game in progress for {username}. Type 'bet <amount>' to begin.")

    async def stand(self, user):
        username = user.username
        if username in self.games:
            await self.dealer_turn(username)
            await self.show_hands(user, show_dealer=True)
            await self.determine_winner(username)
        else:
            await self.highrise.chat(f"No game in progress for {username}. Type 'bet <amount>' to begin.")

    async def dealer_turn(self, username):
        while self.calculate_hand(self.games[username]["dealer_hand"]) < 17:
            self.games[username]["dealer_hand"].append(self.draw_card())

    async def determine_winner(self, username):
        player_score = self.calculate_hand(self.games[username]["player_hand"])
        dealer_score = self.calculate_hand(self.games[username]["dealer_hand"])
        bet_amount = self.bets[username]

        if player_score > 21:
            await self.highrise.chat(f"{username}, you busted! Your balance is now {self.balances[username].amount} gold bars.")
            await self.send_emote("emote-laughing")
            del self.bets[username]
        elif dealer_score > 21 or player_score > dealer_score:
            winnings = bet_amount * 2
            self.balances[username].amount += winnings
            await self.highrise.chat(f"{username}, you win! Your balance is now {self.balances[username].amount} gold bars.")
            await self.send_emote("emote-panic")
            await self.prompt_next_action(username)
        elif player_score < dealer_score:
            await self.highrise.chat(f"{username}, the dealer wins! Your balance is now {self.balances[username].amount} gold bars.")
            await self.send_emote("emote-laughing")
            del self.bets[username]
        else:
            self.balances[username].amount += bet_amount  # Return bet amount on tie
            await self.highrise.chat(f"{username}, it's a tie! Your balance is now {self.balances[username].amount} gold bars.")
            await self.prompt_next_action(username)

        del self.games[username]

    async def prompt_next_action(self, username):
        await self.highrise.chat(f"{username}, would you like to 'cash out' or 'bet again <amount>'?")

    async def bet_again(self, user, bet_amount):
        username = user.username
        if username in self.balances and self.balances[username].amount >= bet_amount:
            self.bets[username] = bet_amount
            self.games[username] = {"player_hand": [], "dealer_hand": []}
            self.balances[username].amount -= bet_amount
            print(f"{username}'s balance after betting again: {self.balances[username].amount}")
            await self.deal_initial_cards(user)
            await self.highrise.chat(f"{username}, you bet again with {bet_amount} gold bars. Your new balance is {self.balances[username].amount} gold bars.")
        else:
            current_balance = self.balances.get(username, CurrencyItem(type='earned_gold', amount=0)).amount
            print(f"{username} tried to bet again with insufficient balance. Current balance: {current_balance}")
            await self.highrise.chat(f"{username}, you need to have enough balance to bet again. Your current balance is {current_balance} gold bars.")

    async def cash_out(self, user: User, amount_to_cash_out=None):
        username = user.username
        if username in self.balances and self.balances[username].amount > 0:
            if amount_to_cash_out is None:
                amount_to_cash_out = self.balances[username].amount
            if amount_to_cash_out > self.balances[username].amount:
                await self.highrise.chat(f"{username}, you don't have enough balance to cash out {amount_to_cash_out} gold bars. Your current balance is {self.balances[username].amount} gold bars.")
                return

            try:
                # Convert amount_to_cash_out to integer
                amount_to_cash_out = int(amount_to_cash_out)
                
                # Determine the gold bar type based on the amount
                bars_dictionary = {10000: "gold_bar_10k", 
                                   5000: "gold_bar_5000",
                                   1000: "gold_bar_1k",
                                   500: "gold_bar_500",
                                   100: "gold_bar_100",
                                   50: "gold_bar_50",
                                   10: "gold_bar_10",
                                   5: "gold_bar_5",
                                   1: "gold_bar_1"}
                tip = []
                remaining_amount = amount_to_cash_out
                for bar in bars_dictionary:
                    if remaining_amount >= bar:
                        bar_amount = remaining_amount // bar
                        remaining_amount -= bar * bar_amount
                        for _ in range(bar_amount):
                            tip.append(bars_dictionary[bar])
                # Tip the user
                for bar in tip:
                    await self.highrise.tip_user(user.id, bar)

                self.balances[username].amount -= amount_to_cash_out
                await self.highrise.chat(f"{username}, you have cashed out {amount_to_cash_out} gold bars. Your balance is now {self.balances[username].amount} gold bars.")
            except Exception as e:
                await self.highrise.chat(f"Error during cash out: {e}")
        else:
            await self.highrise.chat(f"{username}, you have no balance to cash out.")

    async def show_hands(self, user, show_dealer):
        username = user.username
        player_hand = self.games[username]["player_hand"]
        dealer_hand = self.games[username]["dealer_hand"]

        player_hand_str = ", ".join(player_hand)
        dealer_hand_str = ", ".join(dealer_hand) if show_dealer else f"{dealer_hand[0]}, [hidden]"

        await self.whisper(user, f"{username}'s hand: {player_hand_str} (Total: {self.calculate_hand(player_hand)})")
        await self.whisper(user, f"Dealer's hand: {dealer_hand_str}")

    def draw_card(self):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return random.choice(values)

    def calculate_hand(self, hand):
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
        score = sum(values[card] for card in hand)
        aces = hand.count('A')

        while score > 21 and aces:
            score -= 10
            aces -= 1

        return score

    async def on_user_join(self, user: User, position: Position):
        print(f"{user.username} has joined the room at position {position}.")
        await self.highrise.chat(f"Welcome to the room, {user.username}!")
        new_position = Position(x=5.0, y=5.0, z=0.0, facing="FrontRight")
        await self.highrise.walk_to(new_position)
        await self.highrise.chat(f"Welcome! To Bot BlackJack")
        await self.highrise.chat(f"To start playing you have to tip me")
        await self.highrise.chat(f"When you're ready to play say:")
        await self.highrise.chat(f"Bet + [Amount]")
        await self.highrise.chat(f"Hit (to draw card)")
        await self.highrise.chat(f"Stay (to hold)")
        await self.highrise.chat(f"When you want to check your balance say:")
        await self.highrise.chat(f"Balance")
        await self.highrise.chat(f"When you want to cash out say:")
        await self.highrise.chat(f"cash out [Amount] / if you don't mention an amount you will withdraw your full balance")
        await self.highrise.chat(f"Good luck!")

    async def on_tip(self, sender: User, receiver: User, item: CurrencyItem):
        amount = item.amount
        if sender.username in self.balances:
            self.balances[sender.username].amount += amount
        else:
            self.balances[sender.username] = CurrencyItem(type="earned_gold", amount=amount)

        await self.highrise.chat(f"Thank you for the tip, {sender.username}! {sender.username}, your balance is now {self.balances[sender.username].amount} gold bars.")
        print(f"{sender.username}'s new balance after tip: {self.balances[sender.username].amount}")

    async def check_wallet(self):
        wallet = (await self.highrise.get_wallet()).content
        await self.highrise.chat(f"The bot wallet contains {wallet[0].amount} {wallet[0].type}")

    async def check_gold(self):
        wallet = (await self.highrise.get_wallet()).content
        gold = next((item.amount for item in wallet if item.type == 'gold'), 0)
        await self.highrise.chat(f"The bot's gold is {gold}")

    async def check_balance(self, username):
        if username in self.balances:
            current_balance = self.balances[username].amount
            await self.highrise.chat(f"{username}, your current balance is {current_balance} gold bars.")
        else:
            await self.highrise.chat(f"{username}, you have no balance record. Please tip the bot to start.")

    async def send_emote(self, emote_id):
        await self.highrise.send_emote(emote_id)

#last update on bot imtrying to work on its run_bot.py but its still not working taht well, I still need to monitor its function - next function in mind is have an additional bot for greetings in the entrance