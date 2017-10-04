# Classes to be used across both parts of project
from collections import namedtuple
from scipy.stats import poisson
import matplotlib.pyplot as plt
import numpy as np

# Randomly generate bool responses for decision making
randnumbs = list(np.random.poisson(.5, 1000))
def randBool():
    num = randnumbs.pop()
    if (num == 0): return True
    else: return False

bigrandnumbs = list(np.random.poisson(1000, 1000))
def randIndex(length):
    num = bigrandnumbs.pop() % length
    return num

# To be used for structuring operation data
Operation = namedtuple("Operation", "op dataitem")

# Class used for creating transactions to be used in history and schedules
class Transaction:
    def __init__(self, dataitems, numops, completed=True):
        # specifies whether there is an ending abort or commit
        self.completed = completed
        if (len(dataitems) > 5): raise ValueError("Too many data items")
        # operations to be generated randomly by another function and assigned here
        # Operation example: [Operation("r","y"), Operation("w","x")]
        self.operations = self.randGenerateOperations(dataitems,numops)

    def __str__(self):
        output = ""
        for o in self.operations:
            optype, dataitem = o
            if(not dataitem == ""):
                opstring = str(optype)+"("+str(dataitem)+")"
                output += opstring
            else:
                output += optype

        return output

    # Generate transaction operations
    def randGenerateOperations(self,dataitems, numops):
        operations = []
        for i in range(numops):
            op = ""
            if (randBool()): op = "r"
            else: op = "w"
            item = dataitems[0]
            operations.append(Operation(op,item))

        if(self.completed):
            operations.append(Operation(self.randCommitGenerate(),""))

        return operations

    # Generate whether transaction committed or aborted
    def randCommitGenerate(self):
        if (randBool()): return "c"
        else: return "a"


class History():
    def __init__(self, numTrans, dataItems):
        if (numTrans > 5): raise ValueError("Too many transactions")
        self.transactions = self.generateTransactions(numTrans, [])
        self.orderedOperations = self.orderOperations(self.transactions)

    def __str__(self):
        output = "Transactions:\n"
        # Output all of the transactions
        for i in range(len(self.transactions)):
            output += "T"+str(i)+": "+str(self.transactions[i])+"\n"
        output += "\nOrdered History:\n"

        # Output the ordered history
        for o in self.orderedOperations:
            tnum = o[0] # Number of the transaction
            optype, dataitem = o[1] # Operation and its data item
            if(not dataitem == ""):
                opstring = str(optype)+str(tnum)+"("+str(dataitem)+")"
                output += opstring
            else:
                output += optype+str(tnum)

        return output

    def generateTransactions(self, numTrans, dataItems):
        transactions = []
        for i in range(numTrans):
            # Can vary which data items are used in various transactions
            randNumOfOps = self.generateNumTransOps()
            transactions.append(Transaction(dataItems, randNumOfOps))
        return transactions

    # Take list of transactions and randomly order their operations
    def orderOperations(self, transactions):
        # Format [(Transaction index, operation), ... , (Transaction index, operation)]
        # randomly select transaction and pop transactions when list of ops empty
        # continue until no remaining transactions
        return []

    # Randomly generate number of operations for a transaction
    def generateNumTransOps(self):
        rlist = list(np.random.poisson(1000, 100))
        num = rlist.pop() % 5
        return num


class Schedule():
    def __init__(self):
        print "test"

# Testing transaction output
t = Transaction(["x", "y", "z"], 10, completed=True)
print t

rr = list(np.random.poisson(1000, 100))
count, bins, ignored = plt.hist(rr, 14, normed=True)
plt.show()
# total = set()
# for e in list(rr):
#     print (e % 5)
# print(total)

## TODO: need a function that will get random generated number between ranges
## TODO: need a function to randomly select objects from a list
## TODO: fill in all of the random generation functions

