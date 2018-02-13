# donation-analytics

# Introduction

The project works on the data pipeline, aiming to help analyzing loyalty trends in campaign contributions, namely identifying areas of repeat donors and calculating how much they're spending.

A file listing individual campaign contributions for multiple years is given, and the project is designed to find which ones come from repeat donors, calculate total amounts received, total number of contributions received, and donation amount in a given percentile.

# Instructions to run

The program is written in Python. The imported library are pandas, numpy. Dependecies: 

import csv
import pandas as pd
import numpy as np
import datetime
import sys
import time

The run command line is:

python ./src/donation_analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt

# Methodology and Algorithm

The program read in file line by line, and skip records whose fields are empty or malformed. After skipping some records, the program keep the rest of records in list. Then, convert the list to dataframe with columns cmte_id','name','zip_code','transaction_dt','transaction_amt','other_id','transaction_year'. 

Since data flows in a real-time manner, the program iterate the dataframe row by row. 'repeated_donor' column is added to the dataframe to record whether the incoming record is a repeated donor. To find repeated donors, it is assumed that if any transaction year in previous dataframe is smaller than the current dataframe with same cmte_id and zip, then the current record donor is repeated donor, and 'repeated_donor' column is marked as true. If the current record donor is repeated donor,then group dataframe by cmte_id, zip_code, and transaction_year. Add the number and amount to the total_ columns, and then sort amount column, calculate the percentile value, and assign it to percentile column.





