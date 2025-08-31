import gradio as gr
import pandas as pd
from decimal import Decimal

# Import the backend class and exceptions from the accounts.py file
# This file (app.py) must be in the same directory as accounts.py
try:
    from accounts import Account, InsufficientFundsError, InsufficientSharesError, UnknownSymbolError
except ImportError:
    print("Error: The 'accounts.py' file was not found in the same directory.")
    print("Please make sure both app.py and accounts.py are in the same folder.")
    exit()

# --- 1. State Management and Initialization ---

def create_initial_account():
    """
    Creates a new account instance for the Gradio session.
    For this demo, we start the user with a $10,000 deposit.
    """
    account = Account(user_id="demo_user")
    account.deposit(10000)
    return account

# --- 2. UI Helper Functions ---

def update_all_displays(account: Account):
    """
    Takes an Account object and returns formatted data for all display components.
    This centralizes the UI update logic.
    """
    # Format the main stats with dollar signs and commas
    cash_str = f"${account.cash_balance:,.2f}"
    portfolio_value_str = f"${account.get_portfolio_value():,.2f}"
    pnl_str = f"${account.get_profit_or_loss():,.2f}"

    # Create a DataFrame for current holdings
    holdings_data = account.get_holdings()
    if holdings_data:
        holdings_df = pd.DataFrame(list(holdings_data.items()), columns=['Symbol', 'Quantity'])
    else:
        # Provide an empty DataFrame with correct headers if no holdings
        holdings_df = pd.DataFrame({'Symbol': [], 'Quantity': []})

    # Create a DataFrame for transaction history
    transactions_list = account.get_transaction_history()
    if transactions_list:
        # Convert the list of Transaction objects into a list of dictionaries
        tx_data = [
            {
                "Time": tx.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "Type": tx.type,
                "Symbol": tx.symbol if tx.symbol else '---',
                "Quantity": tx.quantity if tx.quantity is not None else '---',
                "Share Price": f"${tx.share_price:,.2f}" if tx.share_price else '---',
                "Total Amount": f"${tx.amount:,.2f}"
            }
            # Show most recent transactions first
            for tx in reversed(transactions_list)
        ]
        tx_df = pd.DataFrame(tx_data)
    else:
        # Provide an empty DataFrame if no transactions
        tx_df = pd.DataFrame()

    return cash_str, portfolio_value_str, pnl_str, holdings_df, tx_df

# --- 3. Gradio Event Handlers ---

def handle_deposit(account: Account, amount: float):
    """Event handler for the deposit button."""
    if not amount or amount <= 0:
        gr.Warning("Please enter a positive amount to deposit.")
        # Return current state if input is invalid
        return account, *update_all_displays(account)
    try:
        account.deposit(amount)
        gr.Info(f"Successfully deposited ${amount:,.2f}.")
    except ValueError as e:
        gr.Error(str(e))
    # Return the (potentially updated) account state and all new display values
    return account, *update_all_displays(account)

def handle_withdraw(account: Account, amount: float):
    """Event handler for the withdraw button."""
    if not amount or amount <= 0:
        gr.Warning("Please enter a positive amount to withdraw.")
        return account, *update_all_displays(account)
    try:
        account.withdraw(amount)
        gr.Info(f"Successfully withdrew ${amount:,.2f}.")
    except (InsufficientFundsError, ValueError) as e:
        gr.Error(str(e))
    return account, *update_all_displays(account)

def handle_buy(account: Account, symbol: str, quantity: int):
    """Event handler for the buy button."""
    if not symbol or not quantity or quantity <= 0:
        gr.Warning("Please select a symbol and enter a positive whole number for quantity.")
        return account, *update_all_displays(account)
    try:
        # Gradio Number input can be float, so ensure it's an int
        int_quantity = int(quantity)
        account.buy_shares(symbol, int_quantity)
        gr.Info(f"Successfully bought {int_quantity} share(s) of {symbol}.")
    except (InsufficientFundsError, UnknownSymbolError, ValueError) as e:
        gr.Error(str(e))
    return account, *update_all_displays(account)

def handle_sell(account: Account, symbol: str, quantity: int):
    """Event handler for the sell button."""
    if not symbol or not quantity or quantity <= 0:
        gr.Warning("Please select a symbol and enter a positive whole number for quantity.")
        return account, *update_all_displays(account)
    try:
        int_quantity = int(quantity)
        account.sell_shares(symbol, int_quantity)
        gr.Info(f"Successfully sold {int_quantity} share(s) of {symbol}.")
    except (InsufficientSharesError, UnknownSymbolError, ValueError) as e:
        gr.Error(str(e))
    return account, *update_all_displays(account)

# --- 4. Gradio UI Layout ---

with gr.Blocks(theme=gr.themes.Soft(), title="Trading Account Simulator") as demo:
    # This gr.State object will hold the user's Account instance across interactions
    account_state = gr.State(value=create_initial_account())

    gr.Markdown("# 📈 Trading Account Simulator")
    gr.Markdown("A simple UI to demonstrate a trading account backend. The account starts with a **$10,000** cash balance.")

    # --- Top Row: Key Account Metrics ---
    with gr.Row():
        cash_balance_disp = gr.Textbox(label="Cash Balance", interactive=False)
        portfolio_value_disp = gr.Textbox(label="Total Portfolio Value", interactive=False)
        pnl_disp = gr.Textbox(label="Profit / Loss", interactive=False)

    # --- Middle Section: User Actions in Tabs ---
    with gr.Tabs():
        with gr.TabItem("💵 Cash Management"):
            with gr.Row():
                cash_amount_input = gr.Number(label="Amount", minimum=0.01, step=100)
                deposit_btn = gr.Button("Deposit", variant="primary")
                withdraw_btn = gr.Button("Withdraw", variant="stop")

        with gr.TabItem("📊 Trade Stocks"):
            with gr.Row():
                # Dropdown pre-filled with known symbols from the backend
                symbol_input = gr.Dropdown(choices=['AAPL', 'TSLA', 'GOOGL'], label="Stock Symbol")
                quantity_input = gr.Number(label="Quantity", minimum=1, step=1, precision=0)
                buy_btn = gr.Button("Buy", variant="primary")
                sell_btn = gr.Button("Sell", variant="stop")

    # --- Bottom Section: Detailed Reports in Tabs ---
    with gr.Tabs():
        with gr.TabItem("💼 Current Holdings"):
            holdings_df_disp = gr.DataFrame(headers=['Symbol', 'Quantity'], wrap=True)
        with gr.TabItem("📜 Transaction History"):
            tx_history_df_disp = gr.DataFrame(wrap=True)

    # --- 5. Component Connections and Event Listeners ---

    # A list of all display components that need to be updated after any action
    all_display_outputs = [
        cash_balance_disp,
        portfolio_value_disp,
        pnl_disp,
        holdings_df_disp,
        tx_history_df_disp
    ]

    # The list of outputs for action handlers must include the state object itself
    # as the first element, so it gets updated and passed to the next function call.
    handler_outputs = [account_state] + all_display_outputs

    # Connect buttons to their respective handler functions
    deposit_btn.click(fn=handle_deposit, inputs=[account_state, cash_amount_input], outputs=handler_outputs)
    withdraw_btn.click(fn=handle_withdraw, inputs=[account_state, cash_amount_input], outputs=handler_outputs)
    buy_btn.click(fn=handle_buy, inputs=[account_state, symbol_input, quantity_input], outputs=handler_outputs)
    sell_btn.click(fn=handle_sell, inputs=[account_state, symbol_input, quantity_input], outputs=handler_outputs)

    # When the app loads, populate the display components with the initial account data
    demo.load(
        fn=update_all_displays,
        inputs=[account_state],
        outputs=all_display_outputs
    )

if __name__ == "__main__":
    demo.launch()