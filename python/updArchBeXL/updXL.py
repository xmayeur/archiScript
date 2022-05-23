#!/usr/bin/env python
# coding: utf-8

# In[189]:


# ! pip install pandas openpyxl xlsxwriter


# In[1]:


import csv
from os import path, listdir

import openpyxl as xl
from openpyxl.styles import Alignment
from openpyxl.worksheet.datavalidation import DataValidation

# In[6]:


csv_path = r'C:\Users\XY56RE\PycharmProjects\p13596-architecture-model\CSV'
xl_path = r'C:\Users\XY56RE\ING\BE Architecture CoE Application Landscape - General\BE Mainframe Decommissioning'
xl_file = r'BE Mainframe Application Functional Information.xlsx'
out_path = r'C:\Users\XY56RE\PycharmProjects\p13596-architecture-model\mfAppFiles\test'
xl_out = r'text.xlsx'
csv_file = 'AIS_functional_export.csv'

suffix = r' - BE Mainframe Application Functional Information.xlsx'

# In[191]:


# In[7]:


files = listdir(csv_path)

for f in files:
    xl_out = path.join(out_path, f[:3] + suffix)
    print(xl_out)

    wb = xl.load_workbook(path.join(out_path, xl_file), read_only=False)
    wb.save(xl_out)

    ws = wb['Functional']
    row = 2
    with open(path.join(csv_path, f), newline='') as fd:
        for rec in csv.reader(fd, delimiter=';'):
            col = 1
            for c in rec:
                x = ws.cell(row=row, column=col)
                x.value = c
                x.alignment = Alignment(wrap_text=True, vertical='top')
                col += 1
            row += 1

    if row > 2:
        af_dv = DataValidation(type="list", formula1='='+"Functional!$F$3:$F$" + str(row), allow_blank=False)
        bo_dv = DataValidation(type="list", formula1='='+"Functional!$I$3:$I$" + str(row), allow_blank=False)

        ws2 = wb['Interactions']
        ws2.add_data_validation(af_dv)
        af_dv.add("$A$3:$A$459")

        ws2.add_data_validation(bo_dv)
        bo_dv.add("$B$3:$B$459")

    wb.save(xl_out)

# In[192]:
