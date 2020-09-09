from django.shortcuts import render,redirect
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from fuzzywuzzy import process
from django.contrib import messages
import re

# Importing Dataset!
data = pd.read_excel('C:/Data Science/Internship/Data_Netmeds.xlsx')
data.dropna(inplace=True)
data.rename(columns={'Prescription Required':'PrescriptionRequired','Units in Pack': 'UnitsinPack', 'Pack Size': 'PackSize', 'Pack Form': 'PackForm'},inplace=True)

# All unique names stored in one list to forward to function.
medicines_list = data['medName'].unique()

#Function to get medicine upto 100 matches!
def medicine_match(query, choice, limit=100):
    result = process.extract(query, choice, limit=limit)
    return result

# All unique names stored in one list to forward to function.
ingird_list = data['salts'].unique()

#Function to get Ingridients upto 900 matches!
def Ingrid_match(query, choice, limit=300):
    result1 = process.extract(query, choice, limit=limit)
    return result1
 
def Home(request):
    messages.success(request,('Please Wait for Couple of Minutes after Enter. Be Patient!'))
    return render(request, 'index.html')

def Display(request):
    if request.method == 'POST':
        Medname = request.POST['medName']
        Ingrid = request.POST['ingrid']

        # Considering only relevent matches for medicines!
        if Medname!='':
            opt = medicine_match(Medname,medicines_list)
            update = []
            for i in range(len(opt)):
                update.append(opt[i][0])
            string_split = Medname.split()
            matched_medicines = []
            for item in update:
                count = 0
                for str in string_split:
                    if str.lower() in item.lower() and count<=len(string_split):
                        count = count+ 1
                if count >= len(string_split):
                    matched_medicines.append(item)
        else:
            matched_medicines=[]
        # Considering only relevent matches for Ingredients!
        matched_ingrid = []
        if Ingrid != '':
            opt1 = Ingrid_match(Ingrid,ingird_list)
            update1 = []
            for i in range(len(opt1)):
                update1.append(opt1[i][0])
            string1_split = re.split(' [+] ',Ingrid)
            length = len(Ingrid.split(' +'))
            matched_ingrid = []
            for item in update1:
                count = 0
                for strng in string1_split:
                    if strng.lower() in item.lower() and count<=length:
                        count = count+ 1
                if count >= length and count <= length+1:
                    matched_ingrid.append(item)
        else:
            matched_ingrid = []
        # Extracting relevent rows from data.
        if not matched_medicines and matched_ingrid: #If only entered Ingridients. 
            all_row=[]
            for ingridient in matched_ingrid:
                row = data[data['salts']==ingridient]
                all_row.append(row)
                df = pd.concat(all_row)
        elif not matched_ingrid and matched_medicines: #If only entered Medicine name.
            all_row=[]
            for medicine in matched_medicines:
                row = data[data['medName']==medicine]
                all_row.append(row)
                df = pd.concat(all_row)
        elif matched_medicines and matched_ingrid: # If both of the is entered.
            all_row=[]
            all_raw=[]
            for medicine in matched_medicines:
                raw = data[data['medName']== medicine]
                all_raw.append(raw)
                raw_df = pd.concat(all_raw)
            for ingridient in matched_ingrid:
                row = raw_df[raw_df['salts']==ingridient]
                all_row.append(row)
                df = pd.concat(all_row)
        else:
            df = pd.DataFrame()
        all_data=[]
        if df.empty:
            messages.success(request,('No records found!'))
        # To have data to be represented as table on webpage.
        for item in range(df.shape[0]):
            temp = df.iloc[item]
            all_data.append(dict(temp))
        context = {'table_data':all_data}
        return render(request,'index.html',context)
    else:
        messages.success(request,('Please Wait for Couple of Minutes after Enter. Be Patient!'))
        return render(request,'index.html')