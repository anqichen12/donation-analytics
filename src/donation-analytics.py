import csv
import pandas as pd
import numpy as np
import datetime
import sys
import time
import heapq
import math

def check_cmte(cmte_str):
    if cmte_str:
        return True
    return False

def check_name(name_str):
    if name_str!='' and name_str.replace(" ", "").replace(",","").isalpha():
        return True
    return False

def check_zip(zip_str):
    zip_str = zip_str.lstrip()
    if len(zip_str) >= 5 and len(zip_str) <= 9 and zip_str[:5].isdigit():
        return True
    return False

def check_amount(amount_str):
    try:
        float(amount_str)
        return True
    except:
        return False

def check_datetime(date_str):
    try:
        datetime.datetime.strptime(date_str, '%m%d%Y')
        return True
    except ValueError:
        return False
    #transaction date shouldn't beyond today's date
    if date>datetime.datetime.today():
    	return False
    else:
    	return True

def extract_percentile(file):
    with open(file,"r") as fin:
        for line in fin:
            percentile = int(line.split('\n')[0])
    return percentile


def run(file1, file2, outputFile):
    s = ''
    res = []
    hash1 = {} # key: <name, zip>, value: list {repeated, year, amount, cmte_id}
    hash2 = {} # key: <cmte_id, zip, year>, value: list {percentile, total, count,minHeap, maxHeap}
    with open(file1,"r") as fin:
        for line in fin:
            s = s + line
        lst = s.split('\n')
        for s in lst:
            inner = []
            if (s==''):
                continue
            str_arr = s.split('|')
            cmte_id = str_arr[0]
            name = str_arr[7]
            zip_code = str_arr[10]
            transaction_date = str_arr[13]
            transaction_amount = str_arr[14]
            other_id = str_arr[15]
            if check_cmte(cmte_id) == False:
                continue
            if check_name(name) == False:
                continue
            if check_zip(zip_code):
                zip_code = zip_code[:5]
            else:
                continue
            if check_datetime(transaction_date)== False:
                continue
            if check_amount(transaction_amount):
                transaction_amount = int(transaction_amount)
            else:
                continue
            if other_id!='':
                continue
            repeated = False
            year = datetime.datetime.strptime(transaction_date,'%m%d%Y').year
            repeated = hash_repeated(name, zip_code, year, transaction_amount, repeated, cmte_id, hash1)
            percentile = extract_percentile(file2)
            minHeap = MinHeap()
            maxHeap = MaxHeap()
            if repeated==True:
                hash_calculation(cmte_id, zip_code, year, minHeap, maxHeap, transaction_amount, percentile, hash2)
                p = hash2[cmte_id, zip_code, year][0]
                t = hash2[cmte_id, zip_code, year][1]
                c = hash2[cmte_id, zip_code, year][2]
                with open(outputFile,'a') as fout:
                    fout.write(cmte_id+'|'+zip_code+'|'+str(year)+'|'+str(p)+'|'+str(t)+'|'+str(c)+'\n')


def hash_repeated(name, zip_code, year, amount, r, cmte_id, hash1):
    ## function that determine whether the donor is repeat donor
    l = []
    if (name, zip_code) in hash1:
        if year > get_min(hash1[name, zip_code]):
            r = True
            l.append(True) # mark as repeated
        else:
            for i in hash1[name, zip_code]:
                if i[0] == True:
                    r = True
                    l.append(True)
                    break
    else:
        hash1[name,zip_code] = []
        l.append(r)
    l.append(year)
    l.append(amount)
    l.append(cmte_id)
    hash1[name,zip_code].append(l)
    return r

def hash_calculation(cmte_id, zip_code, year, minHeap, maxHeap, amount, percentile, hash2):
    l = []
    total = amount
    count = 1
    if (cmte_id, zip_code, year) in hash2:
        percentile_res = calculate_percentile(percentile,hash2[cmte_id, zip_code, year][3],hash2[cmte_id, zip_code, year][4],amount)
        hash2[cmte_id, zip_code, year][0] = percentile_res
        hash2[cmte_id, zip_code, year][1] = hash2[cmte_id, zip_code, year][1] + amount
        hash2[cmte_id, zip_code, year][2] = hash2[cmte_id, zip_code, year][2] + 1
    else:
        percentile_res = calculate_percentile(percentile, minHeap, maxHeap, amount)
        l.append(percentile_res)
        l.append(total)
        l.append(count)
        l.append(minHeap)
        l.append(maxHeap)
        hash2[cmte_id, zip_code, year] = l


def calculate_percentile(percentile, minHeap, maxHeap, amount):
    ## use minHeap and maxHeap to calculate nth percentile amount. 
    ## maxHeap store elements smaller than or equal to nth percentile.
    ## minHeap store elements larger than nth percentile.
    ## nth percentile is the top element of maxHeap
    if len(maxHeap)== 0 or amount <= maxHeap[0]:
        maxHeap.heappush(amount)
    else:
        minHeap.heappush(amount)
    count = len(maxHeap)+len(minHeap)
    count_percentile = math.ceil(float(count)*(0.01*percentile))
    while count_percentile != len(maxHeap):
        if count_percentile < len(maxHeap):
            minHeap.heappush(maxHeap.heappop())
        else:
            maxHeap.heappush(minHeap.heappop())
    return maxHeap[0]


class MaxHeapObj(object):
  def __init__(self,val): self.val = val
  def __lt__(self,other): return self.val > other.val
  def __eq__(self,other): return self.val == other.val
  def __str__(self): return str(self.val)


class MinHeap(object):
  def __init__(self): self.h = []
  def heappush(self,x): heapq.heappush(self.h,x)
  def heappop(self): return heapq.heappop(self.h)
  def __getitem__(self,i): return self.h[i]
  def __len__(self): return len(self.h)


class MaxHeap(MinHeap):
  def heappush(self,x): heapq.heappush(self.h,MaxHeapObj(x))
  def heappop(self): return heapq.heappop(self.h).val
  def __getitem__(self,i): return self.h[i].val

def get_min(l):
    minimum = l[0][1]
    for i in l:
        minimum = min(minimum, i[1])
    return minimum



def main(argv):
    if len(argv) < 4 :
        print ("Error input arguments!")
        sys.exit(0)
    else:
        inputFile1 = argv[1]
        inputFile2 = argv[2]
        outputFile = argv[3]
        #inputFile1 = './input/test2.txt'
        #inputFile2 = './input/percentile.txt'
        #outputFile = './output/repeat_donors.txt'
    fout = outputFile
    contribute = run(inputFile1, inputFile2, outputFile)

if __name__=="__main__":
    start_time = time.time()
    argv = sys.argv
    main(argv)
    #main('python ./src/donation-analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt')
    print("--- %s seconds ---" % (time.time() - start_time))
