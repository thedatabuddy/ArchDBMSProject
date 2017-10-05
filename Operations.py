from collections import namedtuple
import numpy as np
import copy

# Objects to create schedules and histories for later analysis

# Notes: For each history and schedule you specify the number of
# transactions you would like and the potential data items to be used
# from there it will randomly select a subset of those data items for each
# transaction. The number of operations for each transaction is randomly generated
# in addition to what operations they will have and what order those operations
# will appear in the final history/schedule. Histories and schedules are materially
# the same except it is randomly determined whether the transactions in a schedule
# will have an ending event (c or a) or not.

# Currently number of transactions and data items is artificially limited to 5

# Randomly generate bool responses for decision making
randnumbs = list(np.random.poisson(.5, 1000))
def randBool():
    num = randnumbs.pop()
    if (num == 0): return True
    else: return False

# Randomly generate number between 0 and length-1
bigrandnumbs = list(np.random.poisson(1000, 1000))
def randIndex(length):
    num = bigrandnumbs.pop() % length
    return num

# Randomly select a key from the given map
def randKey(map):
    mkeys = map.keys()
    index = randIndex(len(mkeys))
    return mkeys[index]

# To be used for structuring operation data
Operation = namedtuple("Operation", "op dataitem")

# Class used for creating transactions to be used in history and schedules
class Transaction:
    def __init__(self, dataitems, numops, completed=True):
        # Specifies whether there is an ending abort or commit
        self.completed = completed
        if (len(dataitems) > 5): raise ValueError("Too many data items")
        # Operation example: [Operation("r","y"), Operation("w","x")]
        self.operations = self.randGenerateOperations(dataitems,numops)

    # For outputting transactions
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

    def __len__(self):
        return len(self.operations)

    def __getitem__(self, i):
        return self.operations[i]

    def remove(self, i):
        self.operations.pop(i)

    def pop(self, i=0):
        return self.operations.pop(i)

    # Generate transaction operations
    def randGenerateOperations(self,dataitems, numops):
        operations = []
        for i in range(numops):
            op = ""
            if (randBool()): op = "r"
            else: op = "w"
            item = dataitems[randIndex(len(dataitems))]
            operations.append(Operation(op,item))

        if(self.completed):
            operations.append(Operation(self.randCommitGenerate(),""))

        return operations

    # Generate whether transaction committed or aborted
    def randCommitGenerate(self):
        if (randBool()): return "c"
        else: return "a"


class History():
    def __init__(self, numTrans, possibleDataItems):
        if (numTrans > 5): raise ValueError("Too many transactions")
        # Randomly generate transactions then randomly order them
        self.transactions = self.generateTransactions(numTrans, possibleDataItems)
        self.orderedOperations = self.orderOperations(self.transactions)

    # For printing
    def __str__(self):
        output = "Transactions:\n"
        # Output all of the transactions
        for i in self.transactions.keys():
            output += "T"+str(i+1)+": "+str(self.transactions[i])+"\n"
        output += "\nOrdered Operations:\n"

        # Output the ordered history
        for o in self.orderedOperations:
            tnum = o[0] # Index of the transaction
            optype, dataitem = o[1] # Operation and its data item
            if(not dataitem == ""): # if not ending operation (c or a)
                opstring = str(optype)+str(tnum+1)+"("+str(dataitem)+")"
                output += opstring
            else:
                output += optype+str(tnum+1)

        return output

    # Randomly generate the transactions for the history
    def generateTransactions(self, numTrans, possibleDataItems):
        transactions = {}
        for i in range(numTrans):
            # Randomly selects subset of data items to be used
            randDataItemSubset = self.getRandSubset(possibleDataItems)
            # Randomly generates the number of operations in the transaction (currently limited to 5)
            randNumOfOps = self.generateNumTransOps()
            transactions[len(transactions.keys())] = Transaction(randDataItemSubset, randNumOfOps)

        return transactions

    # Take list of transactions and randomly order their operations
    def orderOperations(self, transactions):
        # Format {Transaction index => operation, ... , Transaction index => operation}
        # randomly select transaction and pop transactions when list of ops empty
        # continue until no remaining transactions
        operations = []
        temptrans = copy.deepcopy(transactions)
        while(len(temptrans) != 0):
            # rt -> remaining transactions, ct -> current transaction
            tindex = randKey(temptrans)
            currenttrans = temptrans[tindex]
            # Make sure not empty
            if(len(currenttrans) == 0):
                temptrans.pop(tindex)
                continue
            op = currenttrans.pop()
            operations.append((tindex, op))


        return operations

    # Selects random subset of the dataitems list
    def getRandSubset(self, dataitems):
        outitems = []
        tmpitems = copy.deepcopy(dataitems)
        numitems = randIndex(5)+1 # number between 1 and 5 inclusive
        for i in range(numitems):
            if (len(tmpitems) == 0):
                break
            # pop a random data item and add it to output
            item = tmpitems.pop(randIndex(len(tmpitems)))
            outitems.append(item)

        return outitems

    # Randomly generate number of operations for a transaction
    def generateNumTransOps(self):
        rlist = list(np.random.poisson(1000, 100))
        num = (rlist.pop() % 5) + 1 # num between 1 and 5
        return num


class Schedule(History):
    def __init__(self, numTrans, possibleDataItems):
        History.__init__(self, numTrans, possibleDataItems)

    # Randomly generate the transactions for the schedule
    def generateTransactions(self, numTrans, possibleDataItems):
        transactions = {}
        for i in range(numTrans):
            # Randomly selects subset of data items to be used
            randDataItemSubset = self.getRandSubset(possibleDataItems)
            # Randomly generates the number of operations in the transaction (currently limited to 5)
            randNumOfOps = self.generateNumTransOps()
            # Randomly decide if ending event
            completed = randBool()
            transactions[len(transactions.keys())] = Transaction(randDataItemSubset, randNumOfOps, completed)

        return transactions

# Test output
h = History(5, ["x", "y","m","xx","yy","zz","kk"])
print h
print
s = Schedule(5, ["x", "y","m","xx","yy","zz","kk"])
print s

