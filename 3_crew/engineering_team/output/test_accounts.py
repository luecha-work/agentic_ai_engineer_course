import unittest
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
# No need for sys and os path manipulation, assuming test_accounts.py is in the same directory as accounts.py

from accounts import (
    Account,
    Transaction,
    InsufficientFundsError,
    InsufficientSharesError,
    UnknownSymbolError,
    get_share_price
)

class TestGetSharePrice(unittest.TestCase):

    def test_known_symbols(self):
        self.assertEqual(get_share_price('AAPL'), Decimal('175.25'))
        self.assertEqual(get_share_price('TSLA'), Decimal('250.80'))
        self.assertEqual(get_share_price('GOOGL'), Decimal('135.50'))

    def test_unknown_symbol(self):
        with self.assertRaises(UnknownSymbolError):
            get_share_price('AMZN')

    def test_symbol_case_insensitivity(self):
        self.assertEqual(get_share_price('aapl'), Decimal('175.25'))
        self.assertEqual(get_share_price('TsLa'), Decimal('250.80'))

class TestAccount(unittest.TestCase):

    def setUp(self):
        self.user_id = "test_user"
        self.account = Account(self.user_id)

    def test_init_basic(self):
        self.assertEqual(self.account.user_id, self.user_id)
        self.assertEqual(self.account.cash_balance, Decimal('0.00'))
        self.assertEqual(self.account.total_deposits, Decimal('0.00'))
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(len(self.account.transactions), 0)

    def test_init_with_initial_deposit_float(self):
        account_with_deposit = Account(self.user_id, 1000.50)
        self.assertEqual(account_with_deposit.cash_balance, Decimal('1000.50'))
        self.assertEqual(account_with_deposit.total_deposits, Decimal('1000.50'))
        self.assertEqual(len(account_with_deposit.transactions), 1)
        self.assertEqual(account_with_deposit.transactions[0].type, 'DEPOSIT')
        self.assertEqual(account_with_deposit.transactions[0].amount, Decimal('1000.50'))

    def test_init_with_initial_deposit_string(self):
        account_with_deposit = Account(self.user_id, "1000.75")
        self.assertEqual(account_with_deposit.cash_balance, Decimal('1000.75'))
        self.assertEqual(account_with_deposit.total_deposits, Decimal('1000.75'))

    def test_init_with_zero_initial_deposit(self):
        account_with_deposit = Account(self.user_id, 0.0)
        self.assertEqual(account_with_deposit.cash_balance, Decimal('0.00'))
        self.assertEqual(account_with_deposit.total_deposits, Decimal('0.00'))
        self.assertEqual(len(account_with_deposit.transactions), 0)

    def test_init_invalid_user_id_empty(self):
        with self.assertRaises(ValueError):
            Account("")

    def test_init_invalid_user_id_non_string(self):
        with self.assertRaises(ValueError):
            Account(123)

    def test_deposit_valid_float(self):
        self.account.deposit(500.25)
        self.assertEqual(self.account.cash_balance, Decimal('500.25'))
        self.assertEqual(self.account.total_deposits, Decimal('500.25'))
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0].type, 'DEPOSIT')
        self.assertEqual(self.account.transactions[0].amount, Decimal('500.25'))

    def test_deposit_valid_string(self):
        self.account.deposit("750.80")
        self.assertEqual(self.account.cash_balance, Decimal('750.80'))
        self.assertEqual(self.account.total_deposits, Decimal('750.80'))

    def test_deposit_multiple(self):
        self.account.deposit(100.00)
        self.account.deposit(200.50)
        self.assertEqual(self.account.cash_balance, Decimal('300.50'))
        self.assertEqual(self.account.total_deposits, Decimal('300.50'))
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[0].amount, Decimal('100.00'))
        self.assertEqual(self.account.transactions[1].amount, Decimal('200.50'))

    def test_deposit_zero_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(0)
        self.assertEqual(self.account.cash_balance, Decimal('0.00')) # Should remain unchanged

    def test_deposit_negative_amount(self):
        with self.assertRaises(ValueError):\n            self.account.deposit(-100)
        self.assertEqual(self.account.cash_balance, Decimal('0.00')) # Should remain unchanged

    def test_deposit_quantization(self):
        self.account.deposit(Decimal('100.12345'))
        self.assertEqual(self.account.cash_balance, Decimal('100.12')) # Rounded down

    def test_withdraw_valid(self):
        self.account.deposit(1000)
        self.account.withdraw(250.50)
        self.assertEqual(self.account.cash_balance, Decimal('749.50'))
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1].type, 'WITHDRAW')
        self.assertEqual(self.account.transactions[1].amount, Decimal('250.50'))

    def test_withdraw_insufficient_funds(self):
        self.account.deposit(100)
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(150)
        self.assertEqual(self.account.cash_balance, Decimal('100.00')) # Should remain unchanged

    def test_withdraw_exact_amount(self):
        self.account.deposit(500)
        self.account.withdraw(500)
        self.assertEqual(self.account.cash_balance, Decimal('0.00'))

    def test_withdraw_zero_amount(self):
        self.account.deposit(100)
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
        self.assertEqual(self.account.cash_balance, Decimal('100.00'))

    def test_withdraw_negative_amount(self):
        self.account.deposit(100)
        with self.assertRaises(ValueError):
            self.account.withdraw(-50)
        self.assertEqual(self.account.cash_balance, Decimal('100.00'))

    def test_buy_shares_valid(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 2) # 2 * 175.25 = 350.50
        self.assertEqual(self.account.cash_balance, Decimal('649.50')) # 1000 - 350.50
        self.assertEqual(self.account.holdings, {'AAPL': 2})
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1].type, 'BUY')
        self.assertEqual(self.account.transactions[1].symbol, 'AAPL')
        self.assertEqual(self.account.transactions[1].quantity, 2)
        self.assertEqual(self.account.transactions[1].amount, Decimal('350.50'))
        self.assertEqual(self.account.transactions[1].share_price, Decimal('175.25'))

    def test_buy_shares_multiple_of_same_symbol(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1) # 175.25
        self.account.buy_shares('AAPL', 2) # 350.50
        self.assertEqual(self.account.cash_balance, Decimal('474.25')) # 1000 - 175.25 - 350.50
        self.assertEqual(self.account.holdings, {'AAPL': 3})
        self.assertEqual(len(self.account.transactions), 3)

    def test_buy_shares_different_symbols(self):
        self.account.deposit(2000)
        self.account.buy_shares('AAPL', 1) # 175.25
        self.account.buy_shares('TSLA', 2) # 501.60
        self.assertEqual(self.account.cash_balance, Decimal('1323.15')) # 2000 - 175.25 - 501.60
        self.assertEqual(self.account.holdings, {'AAPL': 1, 'TSLA': 2})

    def test_buy_shares_insufficient_funds(self):
        self.account.deposit(100)
        with self.assertRaises(InsufficientFundsError):
            self.account.buy_shares('AAPL', 1) # Cost 175.25
        self.assertEqual(self.account.cash_balance, Decimal('100.00'))
        self.assertEqual(self.account.holdings, {})

    def test_buy_shares_zero_quantity(self):
        self.account.deposit(1000)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)
        self.assertEqual(self.account.cash_balance, Decimal('1000.00'))

    def test_buy_shares_negative_quantity(self):
        self.account.deposit(1000)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -1)
        self.assertEqual(self.account.cash_balance, Decimal('1000.00'))

    def test_buy_shares_unknown_symbol(self):
        self.account.deposit(1000)
        with self.assertRaises(UnknownSymbolError):
            self.account.buy_shares('AMZN', 1)
        self.assertEqual(self.account.cash_balance, Decimal('1000.00'))

    def test_sell_shares_valid(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 2) # Cost 350.50
        # Cash: 649.50, Holdings: {'AAPL': 2}
        self.account.sell_shares('AAPL', 1) # Revenue 175.25
        self.assertEqual(self.account.cash_balance, Decimal('824.75')) # 649.50 + 175.25
        self.assertEqual(self.account.holdings, {'AAPL': 1})
        self.assertEqual(len(self.account.transactions), 3)
        self.assertEqual(self.account.transactions[2].type, 'SELL')
        self.assertEqual(self.account.transactions[2].symbol, 'AAPL')
        self.assertEqual(self.account.transactions[2].quantity, 1)
        self.assertEqual(self.account.transactions[2].amount, Decimal('175.25'))
        self.assertEqual(self.account.transactions[2].share_price, Decimal('175.25'))

    def test_sell_shares_all_shares(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 2) # Cost 350.50
        # Cash: 649.50, Holdings: {'AAPL': 2}
        self.account.sell_shares('AAPL', 2) # Revenue 350.50
        self.assertEqual(self.account.cash_balance, Decimal('1000.00')) # 649.50 + 350.50
        self.assertEqual(self.account.holdings, {}) # Symbol should be removed

    def test_sell_shares_insufficient_shares(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1)
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares('AAPL', 2)
        self.assertEqual(self.account.cash_balance, Decimal('1000') - Decimal('175.25'))
        self.assertEqual(self.account.holdings, {'AAPL': 1})

    def test_sell_shares_of_unowned_symbol(self):
        self.account.deposit(1000)
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares('GOOGL', 1)
        self.assertEqual(self.account.cash_balance, Decimal('1000.00'))
        self.assertEqual(self.account.holdings, {})

    def test_sell_shares_zero_quantity(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1)
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)
        self.assertEqual(self.account.cash_balance, Decimal('1000') - Decimal('175.25'))

    def test_sell_shares_negative_quantity(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1)
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -1)
        self.assertEqual(self.account.cash_balance, Decimal('1000') - Decimal('175.25'))

    def test_sell_shares_unknown_symbol(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1)
        with self.assertRaises(UnknownSymbolError):
            # This tests that get_share_price is called for the symbol being sold
            self.account.sell_shares('AMZN', 1)
        self.assertEqual(self.account.cash_balance, Decimal('1000') - Decimal('175.25'))

    def test_get_holdings_empty(self):
        self.assertEqual(self.account.get_holdings(), {})

    def test_get_holdings_with_shares(self):
        self.account.deposit(2000)
        self.account.buy_shares('AAPL', 1)
        self.account.buy_shares('TSLA', 2)
        expected_holdings = {'AAPL': 1, 'TSLA': 2}
        self.assertEqual(self.account.get_holdings(), expected_holdings)

    def test_get_holdings_returns_copy(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1)
        holdings_copy = self.account.get_holdings()
        holdings_copy['GOOGL'] = 5 # Modify the copy
        self.assertNotEqual(self.account.holdings, holdings_copy)
        self.assertEqual(self.account.holdings, {'AAPL': 1})

    def test_get_portfolio_value_only_cash(self):
        self.account.deposit(500)
        self.assertEqual(self.account.get_portfolio_value(), Decimal('500.00'))

    def test_get_portfolio_value_with_holdings(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 1) # Cost 175.25, current price 175.25
        self.account.buy_shares('TSLA', 2) # Cost 501.60, current price 250.80
        # Cash: 1000 - 175.25 - 501.60 = 323.15
        # Holdings value: (1 * 175.25) + (2 * 250.80) = 175.25 + 501.60 = 676.85
        # Total: 323.15 + 676.85 = 1000.00
        self.assertEqual(self.account.get_portfolio_value(), Decimal('1000.00'))

    def test_get_portfolio_value_unknown_symbol_in_holdings(self):
        # This scenario shouldn't happen with current buy/sell logic,
        # but if holdings are manually manipulated or price service changes
        self.account.deposit(500)
        self.account.holdings['UNKNOWN'] = 1 # Manually add unknown symbol
        with self.assertRaises(UnknownSymbolError):
            self.account.get_portfolio_value()

    def test_get_profit_or_loss_initial(self):
        self.assertEqual(self.account.get_profit_or_loss(), Decimal('0.00'))

    def test_get_profit_or_loss_after_deposit(self):
        self.account.deposit(1000)
        self.assertEqual(self.account.get_profit_or_loss(), Decimal('0.00')) # 1000 cash - 1000 deposits = 0

    def test_get_profit_or_loss_after_buy(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 2) # Cost 350.50
        # Cash 649.50, Holdings: {'AAPL': 2} (value 350.50)
        # Portfolio value: 649.50 + 350.50 = 1000.00
        # P/L: 1000.00 - 1000.00 = 0
        self.assertEqual(self.account.get_profit_or_loss(), Decimal('0.00'))

    def test_get_profit_or_loss_after_sell(self):
        self.account.deposit(1000)
        self.account.buy_shares('AAPL', 2) # Cost 350.50
        self.account.sell_shares('AAPL', 1) # Sold for 175.25
        # Cash: 649.50 + 175.25 = 824.75
        # Holdings: {'AAPL': 1} (value 175.25)
        # Portfolio value: 824.75 + 175.25 = 1000.00
        # P/L: 1000.00 - 1000.00 = 0
        self.assertEqual(self.account.get_profit_or_loss(), Decimal('0.00'))

    # Note: Profit/Loss only occurs if external share prices change
    # or if we introduce fees/commissions. With current static prices and no fees,
    # P/L is always 0 if all shares are held at their original price.
    # It tracks overall gain/loss relative to total deposits. With static prices,
    # total deposits = current portfolio value always.
    # This test ensures the calculation itself is correct assuming static prices.

    def test_get_transaction_history_empty(self):
        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 0)
        self.assertIsInstance(history, list)

    def test_get_transaction_history_with_transactions(self):
        self.account.deposit(100)
        self.account.buy_shares('AAPL', 1)
        self.account.withdraw(50)
        self.account.sell_shares('AAPL', 1)

        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 4)

        self.assertEqual(history[0].type, 'DEPOSIT')
        self.assertEqual(history[0].amount, Decimal('100.00'))
        self.assertIsInstance(history[0].timestamp, datetime)

        self.assertEqual(history[1].type, 'BUY')
        self.assertEqual(history[1].symbol, 'AAPL')
        self.assertEqual(history[1].quantity, 1)
        self.assertEqual(history[1].amount, Decimal('175.25'))
        self.assertEqual(history[1].share_price, Decimal('175.25'))

        self.assertEqual(history[2].type, 'WITHDRAW')
        self.assertEqual(history[2].amount, Decimal('50.00'))

        self.assertEqual(history[3].type, 'SELL')
        self.assertEqual(history[3].symbol, 'AAPL')
        self.assertEqual(history[3].quantity, 1)
        self.assertEqual(history[3].amount, Decimal('175.25'))
        self.assertEqual(history[3].share_price, Decimal('175.25'))

    def test_get_transaction_history_returns_copy(self):
        self.account.deposit(100)
        history_copy = self.account.get_transaction_history()
        self.account.withdraw(50)
        self.assertNotEqual(len(self.account.transactions), len(history_copy))
        self.assertEqual(len(history_copy), 1)
        self.assertEqual(len(self.account.transactions), 2)

    def test_quantize_decimal_precision(self):
        # Accessing a 'protected' method for explicit testing of its behavior
        quantized = self.account._quantize_decimal(Decimal('123.4567'))
        self.assertEqual(quantized, Decimal('123.45'))
        self.assertIsInstance(quantized, Decimal)

        quantized = self.account._quantize_decimal(Decimal('100'))
        self.assertEqual(quantized, Decimal('100.00'))

        quantized = self.account._quantize_decimal(Decimal('10.999'))
        self.assertEqual(quantized, Decimal('10.99'))

if __name__ == '__main__':
    unittest.main()