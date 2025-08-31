# Design Document: `accounts.py` Module

## 1. Overview

This document provides a detailed design for the `accounts.py` module. This module will provide a self-contained `Account` class for a trading simulation platform. The class will manage a user's cash balance, share holdings, and transaction history. It will support depositing and withdrawing funds, buying and selling shares, and reporting on portfolio value, holdings, and profit/loss.

The design is intended for a backend developer to implement directly. All logic will be encapsulated within the single `accounts.py` file.

## 2. Module: `accounts.py`

This module will contain all the necessary components: custom exceptions, a helper function for share prices, a data class for transactions, and the main `Account` class.

### 2.1. Dependencies

The module will require the following standard Python libraries.

```python
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Literal, Union
from dataclasses import dataclass, field
```

### 2.2. Custom Exceptions

To provide clear, specific errors, we will define custom exception classes.

```python
class InsufficientFundsError(Exception):
    """Raised when an operation cannot be completed due to insufficient cash."""
    pass

class InsufficientSharesError(Exception):
    """Raised when trying to sell more shares than are owned."""
    pass

class UnknownSymbolError(Exception):
    """Raised when a price is requested for an unknown stock symbol."""
    pass
```

### 2.3. Helper Functions

#### `get_share_price(symbol: str) -> Decimal`

This function will fetch the current market price for a given stock symbol. As required, a test implementation with fixed prices will be included directly in the module.

*   **Description:** Takes a stock symbol `str` and returns its current price as a `Decimal`.
*   **Parameters:**
    *   `symbol` (str): The stock ticker symbol (e.g., 'AAPL').
*   **Returns:**
    *   `Decimal`: The price per share.
*   **Raises:**
    *   `UnknownSymbolError`: If the symbol is not in the predefined list.
*   **Implementation Detail:** The function should be case-insensitive regarding the symbol.

```python
# Example implementation to be included in the module
def get_share_price(symbol: str) -> Decimal:
    """
    A test implementation of a share price service.
    Returns a fixed price for a known set of symbols.
    """
    prices = {
        'AAPL': Decimal('175.25'),
        'TSLA': Decimal('250.80'),
        'GOOGL': Decimal('135.50'),
    }
    price = prices.get(symbol.upper())
    if price is None:
        raise UnknownSymbolError(f"No price available for symbol '{symbol}'")
    return price
```

### 2.4. Data Structures

#### `Transaction` Dataclass

To maintain a clean and structured history of all account activities, a `dataclass` will be used.

```python
@dataclass
class Transaction:
    """
    Represents a single transaction in the user's account history.
    """
    timestamp: datetime
    type: Literal['DEPOSIT', 'WITHDRAW', 'BUY', 'SELL']
    amount: Decimal
    symbol: str = None
    quantity: int = None
    share_price: Decimal = None
    
    # Using a default_factory to ensure each instance gets a unique timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow, init=False)

```

## 3. Class: `Account`

This is the main class of the module, encapsulating all the logic for a single user's trading account.

### 3.1. Class Attributes and `__init__`

The constructor will initialize the account's state.

*   **Description:** Creates a new trading account for a user.
*   **Parameters:**
    *   `user_id` (str): A unique identifier for the account holder.
    *   `initial_deposit` (Union[float, str]): The optional starting cash balance. It will be converted to a `Decimal`. Defaults to `0.0`.
*   **Instance Attributes:**
    *   `user_id` (str): Stores the user's identifier.
    *   `cash_balance` (Decimal): The current available cash. Uses `Decimal` for precision.
    *   `total_deposits` (Decimal): The cumulative sum of all deposits. This is the cost basis for P/L calculations.
    *   `holdings` (Dict[str, int]): A dictionary mapping stock symbols to the quantity of shares owned. e.g., `{'AAPL': 10}`.
    *   `transactions` (List[Transaction]): An ordered list of all transactions that have occurred in the account.

```python
class Account:
    """
    Manages a user's trading account, including cash, holdings, and transactions.
    """
    def __init__(self, user_id: str, initial_deposit: Union[float, str] = 0.0):
        # ... implementation ...
```

### 3.2. Methods

#### `deposit(self, amount: Union[float, str]) -> None`

*   **Description:** Adds funds to the account's cash balance.
*   **Parameters:**
    *   `amount` (Union[float, str]): The amount of cash to deposit. Must be a positive value.
*   **Raises:**
    *   `ValueError`: If the `amount` is not a positive number.
*   **Side Effects:**
    *   Increases `self.cash_balance`.
    *   Increases `self.total_deposits`.
    *   Appends a `DEPOSIT` `Transaction` to `self.transactions`.

#### `withdraw(self, amount: Union[float, str]) -> None`

*   **Description:** Withdraws funds from the account's cash balance.
*   **Parameters:**
    *   `amount` (Union[float, str]): The amount of cash to withdraw. Must be a positive value.
*   **Raises:**
    *   `ValueError`: If the `amount` is not a positive number.
    *   `InsufficientFundsError`: If the withdrawal amount is greater than the current `cash_balance`.
*   **Side Effects:**
    *   Decreases `self.cash_balance`.
    *   Appends a `WITHDRAW` `Transaction` to `self.transactions`.

#### `buy_shares(self, symbol: str, quantity: int) -> None`

*   **Description:** Purchases a specified quantity of shares for a given stock symbol.
*   **Parameters:**
    *   `symbol` (str): The stock ticker symbol to buy.
    *   `quantity` (int): The number of shares to purchase. Must be a positive integer.
*   **Raises:**
    *   `ValueError`: If `quantity` is not a positive integer.
    *   `UnknownSymbolError`: If the `symbol` price cannot be retrieved.
    *   `InsufficientFundsError`: If the total cost (`quantity` * `price`) exceeds the `cash_balance`.
*   **Side Effects:**
    *   Calls `get_share_price()` to determine the cost.
    *   Decreases `self.cash_balance` by the total cost.
    *   Increases the share count for the `symbol` in `self.holdings`.
    *   Appends a `BUY` `Transaction` to `self.transactions`.

#### `sell_shares(self, symbol: str, quantity: int) -> None`

*   **Description:** Sells a specified quantity of owned shares for a given stock symbol.
*   **Parameters:**
    *   `symbol` (str): The stock ticker symbol to sell.
    *   `quantity` (int): The number of shares to sell. Must be a positive integer.
*   **Raises:**
    *   `ValueError`: If `quantity` is not a positive integer.
    *   `UnknownSymbolError`: If the `symbol` price cannot be retrieved.
    *   `InsufficientSharesError`: If the user tries to sell more shares of a `symbol` than they own.
*   **Side Effects:**
    *   Calls `get_share_price()` to determine the sale value.
    *   Increases `self.cash_balance` by the total value.
    *   Decreases the share count for the `symbol` in `self.holdings`.
    *   Appends a `SELL` `Transaction` to `self.transactions`.

#### `get_holdings(self) -> Dict[str, int]`

*   **Description:** Returns a copy of the user's current share holdings.
*   **Returns:**
    *   `Dict[str, int]`: A dictionary mapping symbols to the quantity of shares owned.

#### `get_portfolio_value(self) -> Decimal`

*   **Description:** Calculates the total current value of the account, including cash and the market value of all share holdings.
*   **Returns:**
    *   `Decimal`: The total portfolio value (`cash_balance` + sum of (`quantity` * `current_price`) for all holdings).
*   **Error Handling:** If a price cannot be fetched for an owned symbol, this method should handle it gracefully, possibly by logging a warning and excluding that holding from the total, or by raising an exception. The design choice is to raise an `UnknownSymbolError` to ensure data integrity.

#### `get_profit_or_loss(self) -> Decimal`

*   **Description:** Calculates the total profit or loss of the account. This is the difference between the current portfolio value and the total amount of money deposited by the user.
*   **Returns:**
    *   `Decimal`: The total profit (positive value) or loss (negative value). Calculation is `get_portfolio_value()` - `self.total_deposits`.

#### `get_transaction_history(self) -> List[Transaction]`

*   **Description:** Returns a copy of the list of all transactions for the account.
*   **Returns:**
    *   `List[Transaction]`: An ordered list of `Transaction` objects.

---
**End of Design Document**