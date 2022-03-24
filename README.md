# Get Kli
Saves the last 9 weeks of data to the database via binance
Which periods to save can be selected via the configs file (calculate)
The backtest feature of the retrieved data has been deleted

If the back_test is False in the configs file, data will be retrieved until the current data. If True, data will be captured until the last part of the data in the highest period.

Example taken on 24.03.2022 05:06:00:

back_test = True
>{"1w": {"calculate": False, "check_signal": None},
>
>"1d": {"calculate": True, "check_signal": None},
>
>"12h": {"calculate": False, "check_signal": None},
>
>...
>
>...
>
>"5m": {"calculate": True, "check_signal": None},
>
>"1m": {"calculate": False, "check_signal": None},
>
>}
>
>Last part of 1-day data: 23.03.2022 00:00:00
>
>Last part of 5-minute data: 23.03.2022 23:55:00

back_test = False
>{"1w": {"calculate": False, "check_signal": None},
>
>"1d": {"calculate": True, "check_signal": None},
>
>"12h": {"calculate": False, "check_signal": None},
>
>...
>
>...
>
>"5m": {"calculate": True, "check_signal": None},
>
>"1m": {"calculate": False, "check_signal": None},
>
>}
>
>Last part of 1-day data: 24.03.2022 00:00:00
>
>Last part of 5-minute data: 24.03.2022 05:05:00

Many features have been removed in the shared version, leaving only the base.
