import csv
import pandas as pd
import numpy as np
import datetime
import sys
import time

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


#extract CMTE_ID, NAME, ZIP_CODE, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID from file
def extract_cont(file):
    s = ''
    outer = []
    with open(file,"r") as fin:
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
            # if cmte_id is not empty, append cmte_id
            if check_cmte(cmte_id):
                inner.append(cmte_id)
            else:
                continue
            # if name is not empty or malformed, append name
            if check_name(name):
                inner.append(name)
            else:
                continue
            # if zip_code format is not empty or fewer than five digits, select first 5 numbers
            if check_zip(zip_code):
                zip_code = zip_code[:5]
                inner.append(zip_code)
            else:
                continue
            # if transaction_date is not empty or malformed, append transaction_date
            if check_datetime(transaction_date):
                inner.append(transaction_date)
            else:
                continue
            # if transaction_amount is not empty, append transaction_amount
            if check_amount(transaction_amount):
                inner.append(transaction_amount)
            else:
                continue
            # if other_id is not null, pass the record
            if other_id!='':
                continue
            inner.append(other_id)
            outer.append(inner)
    return outer


def res_df(extract_list,percentile):
    df = pd.DataFrame(extract_list,columns=['cmte_id','name','zip_code','transaction_dt','transaction_amt','other_id']).reset_index()
    df['transaction_dt'] = df['transaction_dt'].apply(lambda x: datetime.datetime.strptime(x,'%m%d%Y'))
    df['repeated_donor'] = False
    df['transaction_amt']=df['transaction_amt'].astype(float)
    df['percentile'] = 0
    df['tot_amt'] = 0
    df['tot_num'] = 0
    df['transaction_year'] = df['transaction_dt']
    df['transaction_year'] = df['transaction_year'].apply(lambda x: x.year)
    for idx, row in df.iterrows():
        previous_df = df[:idx]
        current_df = df[idx:idx+1]
        #find repeated donors
        join_df = previous_df.merge(current_df, on = ['name','zip_code'])
        if (join_df['transaction_year_x']<join_df['transaction_year_y']).any():
            df.loc[idx,'repeated_donor'] = True
        previous_df = df[:idx]
        current_df = df[idx:idx+1]
        #repeated donor contribution
        if (current_df['repeated_donor']==True).any():
            join_df = previous_df[previous_df['repeated_donor']==True].merge(current_df,on=['cmte_id','zip_code','transaction_year'])
            num = 1
            amt = row['transaction_amt']
            p = 0
            for idx2, row2 in join_df.iterrows():
                num = num+1
                amt = amt+float(row2['transaction_amt_x'])
            df.loc[idx,'tot_amt'] = amt
            df.loc[idx,'tot_num'] = num
            #find percentile transaction_amt
            p = int(np.ceil(num*percentile))
            previous_df = df[:idx]
            previous_df = previous_df[previous_df['repeated_donor']==True]
            current_df = df[idx:idx+1]
            current_cmte_id = current_df['cmte_id'].values[0]
            current_zip = current_df['zip_code'].values[0]
            current_year = current_df['transaction_year'].values[0]
            merge_df = previous_df.append(current_df)
            #group contributions by same cmte_id, zip_code, transaction_year
            group_df = merge_df[(merge_df['cmte_id']==current_cmte_id) & (merge_df['zip_code']==current_zip) & (merge_df['transaction_year']==current_year)]
            group_df = group_df.sort_values(['transaction_amt'],ascending=1)
            #slice row equal to p and get percentile amount
            percent_value = np.percentile(group_df['transaction_amt'],percentile,interpolation='nearest')
            df.loc[idx,'percentile'] = percent_value
    df = df[df['repeated_donor']==True].reset_index()
    return df

def main(argv):
    if len(argv) < 4 :
        print ("Error input arguments!")
        sys.exit(0)
    else:
        inputFile1 = argv[1]
        inputFile2 = argv[2]
        outputFile = argv[3]
    contribute = extract_cont(inputFile1)
    percentile = int(extract_percentile(inputFile2))
    result_df = res_df(contribute,percentile)
    fout = open(outputFile, "w")
    for idx, row in result_df.iterrows():
        fout.write(str(result_df['cmte_id'].iloc[idx])+'|'+str(result_df['zip_code'].iloc[idx])+'|'+str(result_df['transaction_year'].iloc[idx])+'|'+str(int(round(result_df['percentile'].iloc[idx])))+'|'+str(int(round(result_df['tot_amt'].iloc[idx])))+'|'+str(result_df['tot_num'].iloc[idx])+'\n')

if __name__=="__main__":
    start_time = time.time()
    argv = sys.argv
    main(argv)
    print("--- %s seconds ---" % (time.time() - start_time))

