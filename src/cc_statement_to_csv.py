import camelot

def IsInside(t1, t2):
    if t1.page != t2.page:
        return False
    b1 = t1._bbox
    b2 = t2._bbox
    return b1[0] >= b2[0] - 1 and b1[1] >= b2[1] - 1 and b1[2] <= b2[2] + 1 and b1[3] <= b2[3] + 1

fname = '/Users/hylke/Downloads/creditcardstatement.pdf'
tables = camelot.read_pdf(fname, flavor='stream', pages='all', ege_tol=500, columns=['94,137,495']*100, split_text=True)

for t in tables:
    if any(t is not tt and IsInside(t, tt) for tt in tables):
        continue
    for idx, row in enumerate(t.data):
        if len(row) != 4:
            continue
        print(idx, "::", row)


