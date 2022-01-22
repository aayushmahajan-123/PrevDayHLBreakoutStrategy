import pandas as pd
import numpy as np
import re
import math
import sys
import os
from datetime import datetime

desired_width=320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',100)


def get_dates():
    folder_name = "/home/nonu/Desktop/data_/BN_FUT"
    arr = os.listdir(folder_name)
    arr = sorted(arr)
    print(arr)
    return arr

def check_expiry(d1,d2):
    d1 = datetime.fromisoformat(d1)
    try:
        d = datetime.fromisoformat(d2)
    except:
        d = datetime.strptime(d2, '%m/%d/%Y')

    if d1.date()==d.date():
        return True
    return False

def check_time_in_range(t,T1,T2):
    Test_Time = datetime.strptime(t, '%H:%M')
    T1 = datetime.strptime(T1, '%H:%M')
    T2 = datetime.strptime(T2, '%H:%M')
    if Test_Time>=T1 and Test_Time<=T2:

        return True
    else :

        return False




def main():
    check_time_in_range("9:25","9:15","10:15")

if __name__=="__main__":
    main()