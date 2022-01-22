import pandas as pd
import numpy as np
import re
import math
import sys
import os
from datetime import datetime
import get_dates

desired_width=320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',100)

def SLhit(SL,Low,High,typeoftrade):
    if typeoftrade == "B":
        return Low<=SL
    else:
        return High>=SL
def extract_time(timestamp):
    pattern = "(\d{2}:\d{2})"
    result = re.findall(pattern,timestamp)
    return result[0]


loc = "/home/nonu/Desktop/data_/BN_FUT/"
dates = get_dates.get_dates()

type_of_trade = "N"
intrade = False
prev_day_high = 0
curr_day_high = 1000000
prev_day_low = 0
curr_day_low = -1000000
pnl = 0
SL = 0
entry = 0

slippage = 0.0002

l=[]

for date in dates:
    df = pd.read_csv(loc+date+"/"+"BANKNIFTY-I.csv")
    Day = df.at[1,'day_of_week']
    isexpiry = get_dates.check_expiry(df.at[1,"datetime"],df.at[1,"expiry_date"])

    metadata = {"Date": date, "Day": Day, "High": 0, "Low": 0, "Close": 0,
                "PrevDayLow": prev_day_low, "PrevDayHigh": prev_day_high,
                "InTrade": intrade, "TypeOfPosition": type_of_trade,
                "LongTrigger":0,"ShortTrigger":0,
                "Entry": entry, "StopLoss": SL, "posValue": 0, "BookedPNL": pnl, "NetVal": 0,
                "logs":""}
    LongTrigger = 0
    ShortTrigger = 0
    prev_day_low = curr_day_low
    curr_day_low = 100000000
    prev_day_high = curr_day_high
    curr_day_high = -10000000

    text =""

    for idx,row in df.iterrows():
        Time = extract_time(row["datetime"])
        L = row["low"]
        H = row["high"]
        O = row["open"]
        C = row["close"]

        # print(date)

        if intrade:
            if SLhit(SL,L,H,type_of_trade):
                print(Time+"--> SLHIT")
                text+=Time+"--> SLHIT   "
                if type_of_trade == "B":
                    if SL < O:
                        pnl += (SL-SL*slippage) - entry
                    else:
                        pnl += (O-O*slippage) - entry
                elif type_of_trade == "S":
                    if SL > 0:
                        pnl += entry - (O+O*slippage)
                    else:
                        pnl += entry - (SL+SL*slippage)
                type_of_trade = "N"
                SL = 0
                intrade = False
                entry = 0

            elif isexpiry and Time == "15:30":
                print(Time+"--> Rollover")
                text+=Time+"--> Rollover    "
                df2 = pd.read_csv(loc + date + "/" + "BANKNIFTY-II.csv")
                new_entry = df2["open"].iloc[-1]
                if type_of_trade == "S":
                    pnl += (new_entry) - (O)
                elif type_of_trade == "B":
                    pnl += (O) - (new_entry)

            elif get_dates.check_time_in_range(Time, "9:15", "10:15"):
                if H >= prev_day_high:
                    LongTrigger = prev_day_high
                if L <= prev_day_low:
                    ShortTrigger = prev_day_low

            else:
                if type_of_trade == "B" and ShortTrigger!=0 and L<=ShortTrigger:
                    print(Time+"--> exit long buy short")
                    text+=Time+"--> exit long buy short     "
                    exitprice = O
                    if ShortTrigger<O:
                        exitprice = ShortTrigger
                    else:
                        exitprice = O
                    type_of_trade = "S"
                    pnl += exitprice - entry
                    entry = exitprice
                    SL = entry + entry*0.01

                elif type_of_trade == "S" and LongTrigger!=0 and H>=LongTrigger:
                    print(Time+"-->exit short buy long")
                    text+=Time+"-->exit short buy long     "
                    exitprice = 0
                    if LongTrigger>O:
                        exitprice = LongTrigger
                    else:
                        exitprice = O
                    type_of_trade = "B"
                    pnl+=entry - exitprice
                    entry = exitprice
                    SL = entry - entry*0.01

        elif not intrade:
           # print(Time)
            if get_dates.check_time_in_range(Time, "9:15", "10:15"):
               # print("inside")
                if H >= prev_day_high:
                    LongTrigger = prev_day_high
                if L <= prev_day_low:
                    ShortTrigger = prev_day_low
            else:
                if LongTrigger!=0 and H>=LongTrigger:
                    print(Time+"--> fresh long")
                    text+=Time+"--> fresh long      "
                    entry = 0
                    if O>LongTrigger:
                        entry = O
                    else:
                        entry = LongTrigger
                    intrade = True
                    SL = entry - entry*0.01
                    type_of_trade = "B"

                elif ShortTrigger!=0 and L<=ShortTrigger:
                    print(Time+"--> fresh short")
                    text+=Time+"--> fresh short     "
                    entry = 0
                    if O<ShortTrigger:
                        entry = O
                    else:
                        entry = ShortTrigger
                    intrade = True
                    SL = entry + entry*0.01
                    type_of_trade = "S"

        curr_day_low = min(curr_day_low,L)
        curr_day_high = max(curr_day_high,H)
        metadata["Close"] = C

    metadata["BookedPNL"] = pnl
    metadata["High"] = curr_day_high
    metadata["Low"] = curr_day_low
    metadata["InTrade"] = intrade
    metadata["TypeOfPosition"] = type_of_trade
    metadata["Entry"] = entry
    metadata["StopLoss"] = SL
    metadata["PrevDayLow"] = prev_day_low
    metadata["PrevDayHigh"] = prev_day_high
    metadata["LongTrigger"] = LongTrigger
    metadata["ShortTrigger"] = ShortTrigger
    metadata["logs"] = text
    if type_of_trade == "N":
        metadata["posValue"] = 0
    elif type_of_trade == "B":
        metadata["posValue"] = metadata["Close"] - metadata["Entry"]
    else:
        metadata["posValue"] = metadata["Entry"] - metadata["Close"]

    metadata["NetVal"] = metadata["posValue"] + metadata["BookedPNL"]
    #print(metadata)
    l.append(metadata)

df = pd.DataFrame(l)
print(df)
df.to_excel("/home/nonu/Desktop/data_/"+"PrevDayHLBreakout.xlsx")




