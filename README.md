# Get Kli
Saves the last 9 weeks of data to the database via binance
Which periods to save can be selected via the configs file (calculate)
The backtest feature of the retrieved data has been deleted

If the back_test is False in the configs file, data will be retrieved until the current data. If True, data will be captured until the last part of the data in the highest period.
Example taken on 24.03.2022:
&nbsp;{"1w": {"calculate": False, "check_signal": None},
&nbsp;"1d": {"calculate": True, "check_signal": None},
&nbsp;"12h": {"calculate": False, "check_signal": None},
&nbsp;...
&nbsp;...
&nbsp;"5m": {"calculate": True, "check_signal": None},
&nbsp;"1m": {"calculate": False, "check_signal": None},
&nbsp;}

Last part of 1-day data: 23.03.2022 00:00:00

Last part of 5-minute data: 23.03.2022 23:55:00


Many features have been removed in the shared version, leaving only the base.
