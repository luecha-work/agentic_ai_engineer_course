#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run() -> None:
    """
    Run the crew.
    """
    inputs: dict[str, str] = {"sector": "Technology"}
    # inputs = {"sector": "technology", "notify_email": "luecha.kanm@gmail.com"}

    try:
        result = StockPicker().crew().kickoff(inputs=inputs)

        print("\n\n++ Final Decision++\n\n")
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
