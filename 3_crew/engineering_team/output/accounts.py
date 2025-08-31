# accounts.py

from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Literal, Union
from dataclasses import dataclass, field


# 2.2. Custom Exceptions
class InsufficientFundsError(Exception):
    """Raised when an operation cannot be completed due to insufficient cash."""

    pass


class InsufficientSharesError(Exception):
    """Raised when trying to sell more shares than are owned."""

    pass


class UnknownSymbolError(Exception):
    """Raised when a price is requested for an unknown stock symbol."""

    pass


# 2.3. Helper Functions
def get_share_price(symbol: str) -> Decimal:
    """
    A test implementation of a share price service.
    Returns a fixed price for a known set of symbols.
    """
    prices = {
        "AAPL": Decimal("175.25"),
        "TSLA": Decimal("250.80"),
        "GOOGL": Decimal("135.50"),
    }
    price = prices.get(symbol.upper())
    if price is None:
        raise UnknownSymbolError(f"No price available for symbol '{symbol}'")
    return price


# 2.4. Data Structures
@dataclass
class Transaction:
    """
    Represents a single transaction in the user's account history.
    """

    type: Literal["DEPOSIT", "WITHDRAW", "BUY", "SELL"]
    amount: Decimal
    symbol: str = None
    quantity: int = None
    share_price: Decimal = None
    timestamp: datetime = field(default_factory=datetime.utcnow, init=False)


# 3. Class: Account
class Account:
    """
    Manages a user's trading account, including cash, holdings, and transactions.
    """

    def __init__(self, user_id: str, initial_deposit: Union[float, str] = 0.0):
        """
        Creates a new trading account for a user.
        :param user_id: A unique identifier for the account holder.
        :param initial_deposit: The optional starting cash balance.
        """
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("user_id must be a non-empty string.")

        self.user_id: str = user_id
        self.cash_balance: Decimal = Decimal("0.00")
        self.total_deposits: Decimal = Decimal("0.00")
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Transaction] = []

        if float(initial_deposit) > 0.0:
            self.deposit(initial_deposit)

    def _quantize_decimal(self, value: Decimal) -> Decimal:
        """Helper to standardize decimal precision."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    def deposit(self, amount: Union[float, str]) -> None:
        """
        Adds funds to the account's cash balance.
        :param amount: The amount of cash to deposit. Must be a positive value.
        """
        dec_amount = Decimal(str(amount))
        if dec_amount <= 0:
            raise ValueError("Deposit amount must be positive.")

        quantized_amount = self._quantize_decimal(dec_amount)
        self.cash_balance += quantized_amount
        self.total_deposits += quantized_amount
        self.transactions.append(Transaction(type="DEPOSIT", amount=quantized_amount))

    def withdraw(self, amount: Union[float, str]) -> None:
        """
        Withdraws funds from the account's cash balance.
        :param amount: The amount of cash to withdraw. Must be a positive value.
        """
        dec_amount = Decimal(str(amount))
        if dec_amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        quantized_amount = self._quantize_decimal(dec_amount)
        if quantized_amount > self.cash_balance:
            raise InsufficientFundsError("Withdrawal amount exceeds cash balance.")

        self.cash_balance -= quantized_amount
        self.transactions.append(Transaction(type="WITHDRAW", amount=quantized_amount))

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """
        Purchases a specified quantity of shares for a given stock symbol.
        :param symbol: The stock ticker symbol to buy.
        :param quantity: The number of shares to purchase. Must be a positive integer.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        upper_symbol = symbol.upper()
        share_price = get_share_price(upper_symbol)
        total_cost = self._quantize_decimal(share_price * Decimal(quantity))

        if total_cost > self.cash_balance:
            raise InsufficientFundsError(
                f"Cannot afford to buy {quantity} shares of {upper_symbol}. "
                f"Required: ${total_cost}, Available: ${self.cash_balance}"
            )

        self.cash_balance -= total_cost
        self.holdings[upper_symbol] = self.holdings.get(upper_symbol, 0) + quantity
        self.transactions.append(
            Transaction(
                type="BUY",
                amount=total_cost,
                symbol=upper_symbol,
                quantity=quantity,
                share_price=share_price,
            )
        )

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of owned shares for a given stock symbol.
        :param symbol: The stock ticker symbol to sell.
        :param quantity: The number of shares to sell. Must be a positive integer.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        upper_symbol = symbol.upper()
        current_holding = self.holdings.get(upper_symbol, 0)

        if quantity > current_holding:
            raise InsufficientSharesError(
                f"Cannot sell {quantity} shares of {upper_symbol}. "
                f"Only {current_holding} shares are owned."
            )

        share_price = get_share_price(upper_symbol)
        total_value = self._quantize_decimal(share_price * Decimal(quantity))

        self.cash_balance += total_value
        self.holdings[upper_symbol] -= quantity
        if self.holdings[upper_symbol] == 0:
            del self.holdings[upper_symbol]

        self.transactions.append(
            Transaction(
                type="SELL",
                amount=total_value,
                symbol=upper_symbol,
                quantity=quantity,
                share_price=share_price,
            )
        )

    def get_holdings(self) -> Dict[str, int]:
        """
        Returns a copy of the user's current share holdings.
        """
        return self.holdings.copy()

    def get_portfolio_value(self) -> Decimal:
        """
        Calculates the total current value of the account, including cash and the market value of all holdings.
        """
        holdings_value = Decimal("0.00")
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            holdings_value += price * Decimal(quantity)

        total_value = self.cash_balance + self._quantize_decimal(holdings_value)
        return total_value

    def get_profit_or_loss(self) -> Decimal:
        """
        Calculates the total profit or loss of the account based on total deposits.
        """
        portfolio_value = self.get_portfolio_value()
        return portfolio_value - self.total_deposits

    def get_transaction_history(self) -> List[Transaction]:
        """
        Returns a copy of the list of all transactions for the account.
        """
        return list(self.transactions)
