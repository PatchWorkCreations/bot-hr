import unittest
from unittest.mock import AsyncMock, MagicMock
from bot import Bot
from highrise import User, CurrencyItem

class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()
        self.user = User(username="testuser", id="123")

    def test_start_game(self):
        self.bot.highrise = MagicMock()
        self.bot.balances = {self.user.username: CurrencyItem(type="earned_gold", amount=100)}
        self.bot.highrise.chat = AsyncMock()

        self.bot.start_game(self.user.username, 10)

        self.assertIn(self.user.username, self.bot.games)
        self.assertEqual(self.bot.bets[self.user.username], 10)
        self.assertEqual(self.bot.balances[self.user.username].amount, 90)

    def test_cash_out(self):
        self.bot.highrise = MagicMock()
        self.bot.balances = {self.user.username: CurrencyItem(type="earned_gold", amount=100)}
        self.bot.highrise.tip_user = AsyncMock()
        self.bot.highrise.chat = AsyncMock()

        self.bot.cash_out(self.user, 50)

        self.assertEqual(self.bot.balances[self.user.username].amount, 50)
        self.bot.highrise.tip_user.assert_called_with(self.user.id, "gold_bar_50")

if __name__ == "__main__":
    unittest.main()
