# donation-analytics

# Introduction

The project works on the data pipeline, aiming to help analyzing loyalty trends in campaign contributions, namely identifying areas of repeat donors and calculating how much they're spending.

A file listing individual campaign contributions for multiple years is given, and the project is designed to find which ones come from repeat donors, calculate total amounts received, total number of contributions received, and donation amount in a given percentile.

# Instructions to run

The program is written in Python. The imported library are pandas, numpy. Dependecies: Python 3

import csv
import pandas as pd
import numpy as np
import datetime
import sys
import time

The run command line is:

python ./src/donation_analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt

# Methodology and Algorithm

1. Data Cleaning:

The program read in file line by line, and skip records whose fields are empty or malformed.

2. Find repeated donors

Data Structure: HashMap

Time Complexity: O(1)
Space Complexity: O(n)

The program used two HashMap, where the first HashMap find repeated donors and the second HashMap store calculated value. 

HashMap1 Key: name, zip code, value: list {repeated, year, amount, cmte_id}
HashMap2 Key: cmte_id, zip, year, value: list {percentile, total, count,minHeap, maxHeap}


3. Calculate given percentile value

Data Structure: PriorityQueue

Time complexity: O(log(n))
Space complexity: O(n)

Since data flows in a real-time manner, the program used priorityqueue with minheap and maxheap to calculate given percentile value. maxHeap is used to store elements smaller than or equal to nth percentile. minHeap store elements larger than nth percentile. The given percentile value is maintained as the top element of maxHeap. The aglolrithm is if incoming amount is smaller than top element of maxHeap, then add it to maxHeap. If it is larger than top element of minHeap, then add it to minHeap. At the meantime, maintain the count of maxHeap to be consistent with given percentile count.







