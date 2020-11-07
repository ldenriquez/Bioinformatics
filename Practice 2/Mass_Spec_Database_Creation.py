#!/usr/bin/env python
# coding: utf-8

# ## Task 1
# **Prompt:** Design a database to organize/store the data in dataset1.xlsx and dataset2.xlsx
# 
# **Author:** Lauren Enriquez
# 
# **Notes:** sqlite3 was used to established connections to SQL to create a database. The database is labeled as **Mass_Spec_Database.db**. Any elements in .xlsx files that are empty are written as **0.0** in the database.

# In[1]:


# Wrappers for supported file formats
import string
import sqlite3
from sqlite3 import Error
import pandas as pd
import pyodbc
import numpy as np
import xlrd


# In[2]:


# Establishes connection to SQL database
conn = sqlite3.connect('Mass_Spec_Database.db')
c = conn.cursor()


# In[3]:


# Execution to drop tables was used in the development of the database, does not need to be called everytime
# Statements may be commented out
conn.execute("DROP TABLE Dataset1_RawData;")
conn.execute("DROP TABLE Dataset2_RawData;")
conn.execute("DROP TABLE Dataset2_GroupInfo;")
conn.execute("DROP TABLE Dataset1_GroupInfo;")
conn.commit()


# In[4]:


# Creates Tables with RawData and GroupInfo from each Dataset
c.execute("""CREATE TABLE Dataset1_RawData (Protein TEXT,
                                 S1 REAL,
                                 S2 REAL,
                                 S3 REAL,
                                 S4 REAL,
                                 S5 REAL,
                                 S6 REAL);""")

c.execute("""CREATE TABLE Dataset1_GroupInfo (SampleID TEXT,
                                 GroupID TEXT);""")

c.execute("""CREATE TABLE Dataset2_RawData (Protein TEXT,
                                 SS1 REAL,
                                 SS2 REAL,
                                 SS3 REAL,
                                 SS4 REAL,
                                 SS5 REAL,
                                 SS6 REAL,
                                 SS7 REAL,
                                 SS8 REAL);""")

c.execute("""CREATE TABLE Dataset2_GroupInfo (SampleID TEXT,
                                 GroupID TEXT);""")
# Save (commit) the changes
conn.commit()


# In[5]:


# Uploads data from excel files and stores information on each sheet as dataframes (using pandas)
# Dataset 1
xls1 = pd.ExcelFile('Data/Dataset1.xlsx')
df1 = pd.read_excel(xls1, 'RawData')
df2 = pd.read_excel(xls1, 'GroupInfo')

# Dataset 2
xls2 = pd.ExcelFile('Data/Dataset2.xlsx')
df3 = pd.read_excel(xls2, 'RawData')
df4 = pd.read_excel(xls2, 'GroupInfo')


# In[6]:


# Uploads dataframes into database tables
# Dataset 1
df1.to_sql('Dataset1_RawData', conn, if_exists = 'replace', index = False)
df2.to_sql('Dataset1_GroupInfo', conn, if_exists = 'replace', index = False)

# Dataset 2
df3.to_sql('Dataset2_RawData', conn, if_exists = 'replace', index = False)
df4.to_sql('Dataset2_GroupInfo', conn, if_exists = 'replace', index = False)


# In[7]:


# Function to determine the correct sqlite3 statement to deploy for dataset 1
def column_selection(index):
    if index == 1:
        x = "UPDATE Dataset1_RawData SET S1 = 0.0"
    if index == 2:
        x = "UPDATE Dataset1_RawData SET S2 = 0.0"
    if index == 3:
        x = "UPDATE Dataset1_RawData SET S3 = 0.0"
    if index == 4:
        x = "UPDATE Dataset1_RawData SET S4 = 0.0"
    if index == 5:
        x = "UPDATE Dataset1_RawData SET S5 = 0.0"
    if index == 6:
        x = "UPDATE Dataset1_RawData SET S6 = 0.0"
    return (x);


# In[8]:


# Function to determine the correct sqlite3 statement to deploy for dataset 2
def column_selection2(index):
    if index == 1:
        x = "UPDATE Dataset2_RawData SET SS1 = 0.0"
    if index == 2:
        x = "UPDATE Dataset2_RawData SET SS2 = 0.0"
    if index == 3:
        x = "UPDATE Dataset2_RawData SET SS3 = 0.0"
    if index == 4:
        x = "UPDATE Dataset2_RawData SET SS4 = 0.0"
    if index == 5:
        x = "UPDATE Dataset2_RawData SET SS5 = 0.0"
    if index == 6:
        x = "UPDATE Dataset2_RawData SET SS6 = 0.0"
    if index == 7:
        x = "UPDATE Dataset2_RawData SET SS7 = 0.0"
    if index == 8:
        x = "UPDATE Dataset2_RawData SET SS8 = 0.0"
    return (x);


# In[12]:


# Iterates through each row in the table Dataset1_RawData to change any "None" or empty elements to "0.0"
for row in c.execute("""SELECT * FROM Dataset1_RawData"""):
    protein = row[0];
    index = 0;
    for i in row:
        # Changes the "None" element to "0.0"
        if i is None:
            print(row)
            x = column_selection(index)
            print(x, protein)
            c.execute(x + " WHERE Protein=?",(protein,));
            # Save (commit) the changes       
            conn.commit()
        index += 1;
        
# Save (commit) the changes       
conn.commit()


# In[17]:


# Iterates through each row in the table Dataset2_RawData to change any "None" or empty elements to "0.0"
for row in c.execute("""SELECT * FROM Dataset2_RawData"""):
    protein = row[0];
    index = 0;
    for i in row:
        # Changes the "None" element to "0.0"
        if i is None:
            print(row)
            x = column_selection2(index)
            print(x, protein)
            c.execute(x + " WHERE Protein=?",(protein,));
            # Save (commit) the changes       
            conn.commit()
        index += 1;
        
# Save (commit) the changes       
conn.commit()


# In[19]:


# OUTPUT: Prints Dataset1_RawData and Dataset2_RawData tables to ensure "None" elements are now "0.0"
for row in c.execute("""SELECT * FROM Dataset1_RawData"""):
    print(row)
print("")
for row in c.execute("""SELECT * FROM Dataset2_RawData"""):
    print(row)


# In[20]:


# Closes connection to SQL database 
c.close()

