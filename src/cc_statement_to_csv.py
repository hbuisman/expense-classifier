import camelot
import re
from dateutil import parser
import typing
import pandas
from datetime import date
from enum import Enum

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
            purchase_date = MaybeParseDate(row[1])
            if parsing_state == ParsingState.LOOK_FOR_PAYMENT and purchase_date:
                payment.purchase_date = purchase_date
                payment.description = ParseDescription(row[2])
                payment.amount = float(row[3])
                parsing_state = ParsingState.LOOK_FOR_CATEGORY
            elif parsing_state == ParsingState.LOOK_FOR_CATEGORY:
                payment.category = row[2]
                parsing_state = ParsingState.LOOK_FOR_PAYMENT
                payments.append(payment)
    return payments
                


        
payments = ParsePayments('/Users/hylke/Downloads/creditcardstatement.pdf')
print("Payments parsed: ", len(payments))
                
    
    
