import camelot
import re
from collections import defaultdict
from dateutil import parser
import typing
from typing import Dict
import pandas
from datetime import date
from enum import Enum
from matplotlib import pyplot as plt
import numpy as np

from os import listdir
from os.path import isfile, join
 
 
        

# TODO(hylke): Write unit test based on one page of example pdf.

class ParsingState(Enum):
    LOOK_FOR_PAYMENT = 1
    LOOK_FOR_CATEGORY = 2

class Payment:
    purchase_date: date
    description: str
    category: str
    amount: float

    def ToString(self):
        return "Date: {0} :: Description: {1} :: Category: {2} :: Amount: {3}".format(self.purchase_date,
                self.description, self.category, self.amount)

def ParseDescription(string: str) -> str:
    description_match = re.search("(.*)(\n)?.*", string)
    if description_match:
        return description_match.group(1)
    else:
        return ""


def MaybeParseDate(string: str) -> typing.Optional[date]:
    try:
        purchase_date = parser.parse(
                string,
                parserinfo=parser.parserinfo(dayfirst=True, yearfirst=False))
        return purchase_date
    except parser._parser.ParserError:
        return None


def IsInside(t1, t2):
    if t1.page != t2.page:
        return False
    b1 = t1._bbox
    b2 = t2._bbox
    return b1[0] >= b2[0] - 1 and b1[1] >= b2[1] - 1 and b1[2] <= b2[2] + 1 and b1[3] <= b2[3] + 1

def ParsePayments(filename: str) -> list[Payment]:
    tables = camelot.read_pdf(filename, flavor='stream', pages='all', ege_tol=500, columns=['94,137,495']*100, split_text=True)
    
    payments: list[Payment] = []
    parsing_state = ParsingState.LOOK_FOR_PAYMENT
    
    for t in tables:
        if any(t is not tt and IsInside(t, tt) for tt in tables):
            continue
    
        payment = Payment()
    
        for idx, row in enumerate(t.data):
            if len(row) != 4:
                continue
            print(idx, "::", row)
            accounting_date = MaybeParseDate(row[0])
            purchase_date = MaybeParseDate(row[1])
            if parsing_state == ParsingState.LOOK_FOR_PAYMENT and purchase_date and accounting_date:
                payment.purchase_date = purchase_date
                payment.description = ParseDescription(row[2])
                payment.amount = float(row[3].replace("'", ""))
                parsing_state = ParsingState.LOOK_FOR_CATEGORY
            elif parsing_state == ParsingState.LOOK_FOR_CATEGORY:
                payment.category = row[2]
                parsing_state = ParsingState.LOOK_FOR_PAYMENT
                payments.append(payment)
    return payments
                

def GroupByCategory(payments: list[Payment]) -> Dict[str, float]:
    grouping = defaultdict(float)
    for p in payments:
        # TODO: Fix for negatives.
        if p.amount > 0:
            grouping[p.category] += p.amount
    return grouping

def PlotPaymentGrouping(grouping: defaultdict[float]):
    sorted_grouping = {k: v for k, v in sorted(grouping.items(), key=lambda item: item[1])}
    data = sorted_grouping.values()
    labels = sorted_grouping.keys()
    
    # Creating plot
    fig = plt.figure(figsize =(10, 7))
    plt.pie(data, labels = labels, autopct = '%1.1f%%')
    
    # show plot
    plt.show()

def GetCreditCardStatements(directory: str) -> list[str]:
    onlyfiles = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
    return onlyfiles

files = GetCreditCardStatements('/Users/hylke/Documents/cc_statements/')

payments: list[Payment] = []
for f in files:
    payments.extend(ParsePayments(f))
print("Payments parsed: ", len(payments))
grouping = GroupByCategory(payments)

print(grouping)
PlotPaymentGrouping(grouping)
                
    
    
