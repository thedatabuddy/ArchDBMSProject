from collections import namedtuple
import numpy as np
import copy
import itertools as it
import csv
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
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
conflict_mainpermdict={}
conflict_hispermdict={}
conflict_schpermdict={}
conflict_hisdict={}
conflict_schdict={}
conflict_maindict={}
ordered_operations=""
ordered_history=""
ordered_schedule=""
hisdict={}
hisdict_main={}
schdict={}
hlist=[]
hlist_up=[]
hlist_keys=[]
slist=[]
slist_up=[]
slist_keys=[]
his_permlist=[]
sch_permlist=[]
temp1=0
temp2=0

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
            if (randBool()): op = " R"
            else: op = " W"
            item = dataitems[randIndex(len(dataitems))]
            operations.append(Operation(op,item))

        if(self.completed):
            operations.append(Operation(self.randCommitGenerate(),""))

        return operations

    # Generate whether transaction committed or aborted
    def randCommitGenerate(self):
        if (randBool()): return " C"
        else: return " A"
class History():
    tranlist = {}
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
            trnum="T"+str(i+1)
            self.tranlist[trnum]=str(self.transactions[i])
            output += trnum+": "+ self.tranlist[trnum]+"\n"
        hisdict=self.tranlist


        output += "\nOrdered Operations:\n"

        # Output the ordered history
        for o in self.orderedOperations:
            tnum = o[0] # Index of the transaction
            optype, dataitem = o[1] # Operation and its data item
            global ordered_operations
            if(not dataitem == ""): # if not ending operation (c or a)
                opstring = str(optype)+str(tnum+1)+"("+str(dataitem)+")"
                ordered_operations+=opstring
                output += opstring
            else:
                opstring= optype+str(tnum+1)
                output += opstring
                ordered_operations+=opstring

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
class HistoryGenerator():
    @staticmethod
    def generate():
        # Test output
        Trans = int(input("Enter the Number of Transactions: "))
        h = History(Trans, ["u", "v", "x", "y", "z"])
        print
        print "History", h
        global hisdict
        hisdict=h.tranlist
class ScheduleGenerator():
    @staticmethod
    def generate():
        # Test output
        Trans = int(input("Enter the Number of Transactions: "))
        print
        s = Schedule(Trans, ["u", "v", "x", "y", "z"])
        print "Schedule",s
        global schdict,hisdict

        schdict = s.tranlist
class NewHis:
    @staticmethod
    def hisgen():
        obj1 = HistoryGenerator
        obj1.generate()
        global hisdict_main, hisdict,ordered_operations,ordered_history
        hisdict_main=hisdict
        global hlist,hlist_keys
        hlist=list(hisdict_main.values())
        hlist_keys=list(hisdict_main.keys())
        ordered_history=ordered_operations
class NewSch:
    @staticmethod
    def schgen():
        obj2 = ScheduleGenerator
        obj2.generate()
        global slist,slist_keys,ordered_operations,ordered_schedule,ordered_history
        slist = list(schdict.values())
        slist_keys = list(schdict.keys())
        ordered_schedule=ordered_operations.replace(ordered_history,"")
NewHis.hisgen()
print "\n"
print "\n"
NewSch.schgen()
print "\n"
print "\n"
class ConflictGen():

    def ConflictPairGen(self,his):
        global conflict_maindict
        conflict_maindict[his]={}
        ulist = []
        vlist = []
        xlist = []
        ylist = []
        zlist = []
        oper = []
        uconflict = []
        vconflict = []
        xconflict = []
        yconflict = []
        zconflict = []
        b = his.split(" ")
        for i in b:
            if "u" in i:
                ulist.append(i)
            elif "v" in i:
                vlist.append(i)
            elif "x" in i:
                xlist.append(i)
            elif "y" in i:
                ylist.append(i)
            elif "z" in i:
                zlist.append(i)
            else:
                oper.append(i)

        for i in range(0, len(ulist)):
            for j in range(i + 1, len(ulist)):
                a = ulist[i]
                b = ulist[j]
                # print a,b
                # print a[0]
                if (a[0] == "W"):
                    if (b[1] != a[1]):
                        com = "( " + str(a) + "," + str(b) + ")"
                        if(com not in uconflict):
                            uconflict.append(com)
                elif (a[0] == "R"):
                    if (b[0] == "W"):
                        if (b[1] != a[1]):
                            com = "( " + str(a) + "," + str(b) + ")"
                            if (com not in uconflict):
                                uconflict.append(com)

        conflict_maindict[his]["uconflict"]=uconflict

        for i in range(0, len(vlist)):
            for j in range(i + 1, len(vlist)):
                a = vlist[i]
                b = vlist[j]
                # print a,b
                # print a[0]
                if (a[0] == "W"):
                    if (b[1] != a[1]):
                        com = "( " + str(a) + "," + str(b) + ")"
                        if (com not in vconflict):
                            vconflict.append(com)
                elif (a[0] == "R"):
                    if (b[0] == "W"):
                        if (b[1] != a[1]):
                            com = "( " + str(a) + "," + str(b) + ")"
                            if (com not in vconflict):
                                vconflict.append(com)

        conflict_maindict[his]["vconflict"] = vconflict

        for i in range(0, len(xlist)):
            for j in range(i + 1, len(xlist)):
                a = xlist[i]
                b = xlist[j]
                # print a,b
                # print a[0]
                if (a[0] == "W"):
                    if (b[1] != a[1]):
                        com = "( " + str(a) + "," + str(b) + ")"
                        if (com not in xconflict):
                            xconflict.append(com)
                elif (a[0] == "R"):
                    if (b[0] == "W"):
                        if (b[1] != a[1]):
                            com = "( " + str(a) + "," + str(b) + ")"
                            if (com not in xconflict):
                                xconflict.append(com)

        conflict_maindict[his]["xconflict"] = xconflict
        for i in range(0, len(ylist)):
            for j in range(i + 1, len(ylist)):
                a = ylist[i]
                b = ylist[j]
                # print a,b
                # print a[0]
                if (a[0] == "W"):
                    if (b[1] != a[1]):
                        com = "( " + str(a) + "," + str(b) + ")"
                        if (com not in yconflict):
                            yconflict.append(com)
                elif (a[0] == "R"):
                    if (b[0] == "W"):
                        if (b[1] != a[1]):
                            com = "( " + str(a) + "," + str(b) + ")"
                            if (com not in yconflict):
                                yconflict.append(com)

        conflict_maindict[his]["yconflict"] = yconflict
        for i in range(0, len(zlist)):
            for j in range(i + 1, len(zlist)):
                a = zlist[i]
                b = zlist[j]
                # print a,b
                # print a[0]
                if (a[0] == "W"):
                    if (b[1] != a[1]):
                        com = "( " + str(a) + "," + str(b) + ")"
                        if (com not in zconflict):
                            zconflict.append(com)
                elif (a[0] == "R"):
                    if (b[0] == "W"):
                        if (b[1] != a[1]):
                            com = "( " + str(a) + "," + str(b) + ")"
                            if (com not in zconflict):
                                zconflict.append(com)

        conflict_maindict[his]["zconflict"] = zconflict
a=ConflictGen()
print "conflict pairs of generated history:"
a.ConflictPairGen(ordered_history)
conflict_hisdict[ordered_history]=conflict_maindict[ordered_history]
for k,v in conflict_hisdict[ordered_history].iteritems():
    print k+":" +" "+" ; ".join(v)
print "\n"
print "\n"
print "conflict pairs of generated schedule:"
a.ConflictPairGen(ordered_schedule)
conflict_schdict[ordered_schedule]=conflict_maindict[ordered_schedule]
for k,v in conflict_schdict[ordered_schedule].iteritems():
    print k+":" +" "+" ; ".join(v)
print "\n"
print "\n"


class PermutationGenerator:

    @staticmethod
    def permgen():
        global hlist_keys,hlist,his_permlist
        for i in range(0,len(hlist_keys)):
            word=hlist_keys[i]
            tnum=word[1]
            oldtran=hlist[i]
            oldtranlist=list(oldtran)
            for j in range(0,len(oldtranlist)):
                if oldtranlist[j]=="R" or oldtranlist[j]=="W" or oldtranlist[j]=="C" or oldtranlist[j]=="A":
                    oldtranlist[j]=oldtranlist[j]+tnum
            newtran=''.join(oldtranlist)
            hlist[i]=newtran
        for k in range(0,len(hlist_keys)):
            word=slist_keys[k]
            tnum=word[1]
            oldtran=slist[k]
            oldtranlist=list(oldtran)
            for l in range(0,len(oldtranlist)):
                if oldtranlist[l]=="R" or oldtranlist[l]=="W" or oldtranlist[l]=="C" or oldtranlist[l]=="A":
                    oldtranlist[l]=oldtranlist[l]+tnum
            newtran=''.join(oldtranlist)
            slist[k]=newtran
        for permutation in it.permutations(hlist):
            his_permlist.append(''.join(permutation))

        for permutation in it.permutations(slist):
            sch_permlist.append(''.join(permutation))


obj1=PermutationGenerator()
obj1.permgen()

class HisCompare():
    def compare(self, myList =[], *args):
        for perm in myList:
            b=ConflictGen()
            b.ConflictPairGen(perm)

obj2=HisCompare()
obj2.compare(his_permlist)
for perm in his_permlist:
    conflict_hispermdict[perm]=conflict_maindict[perm]
obj2=HisCompare()
obj2.compare(sch_permlist)
for perm in sch_permlist:
    conflict_schpermdict[perm]=conflict_maindict[perm]

if len(conflict_hisdict[ordered_history]["xconflict"])==0 and len(conflict_hisdict[ordered_history]["yconflict"])==0 and len(conflict_hisdict[ordered_history]["zconflict"])==0 and len(conflict_hisdict[ordered_history]["uconflict"])==0 and len(conflict_hisdict[ordered_history]["vconflict"])==0:
    print"There are no conflict pairs for generated history"
    temp1=1
else:
    v1={}
    for k1,v1 in conflict_hispermdict.iteritems():
        if v1==conflict_hisdict[ordered_history]:
         print "Generated history matches with the serial execution",k1
         temp1=1

if temp1==0:
    print"The conflict pairs of generated history are not in serial order with any of the serial executions, so history is NOT-SERIALIZABLE"
if temp1==1:
    print "Generated history is SERIALIZABLE"


print "\n"
print "\n"

if len(conflict_schdict[ordered_schedule]["xconflict"])==0 and len(conflict_schdict[ordered_schedule]["yconflict"])==0 and len(conflict_schdict[ordered_schedule]["zconflict"])==0 and len(conflict_schdict[ordered_schedule]["uconflict"])==0 and len(conflict_schdict[ordered_schedule]["vconflict"])==0:
    print"There are no conflict pairs for generated schedule"
    temp2=1
else:
    v1={}
    for k1,v1 in conflict_schpermdict.iteritems():
        if v1==conflict_schdict[ordered_schedule]:
         print "Generated schedule matches with the serial execution",k1
         temp2=1

if temp2==0:
    print"The conflict pairs og the generated Schedule are not in serial order with any of the serial executions, so schedule is NOT-SERIALIZABLE"

if temp2==1:
    print "Generated Schedule is SERIALIZABLE"

class Recover():

    def Recover_check(self,his):
        ulist = []
        vlist = []
        xlist = []
        ylist = []
        zlist = []
        oper = []
        reads_from={}
        reads_from2={}
        b = his.split(" ")
        print b
        for i in b:
            if "u" in i:
                ulist.append(i)
            elif "v" in i:
                vlist.append(i)
            elif "x" in i:
                xlist.append(i)
            elif "y" in i:
                ylist.append(i)
            elif "z" in i:
                zlist.append(i)
            else:
                oper.append(i)

        print "u: ", ulist
        print "v: ", vlist
        print "x: ", xlist
        print "y: ", ylist
        print "z: ", zlist
        if '' in oper:
            oper.remove('')

        print "Operations: ", oper
        print "\n\n"

        for i in range(0,len(ulist)):
            sign_temp=0
            temp1=ulist[i]
            if (i+1)<len(ulist):
                temp2 = ulist[i+1]
                if temp1[0]=="W":
                    if temp2[0]=="R" and temp1[1]!=temp2[1]:
                        print "T"+temp2[1]+" reads from T"+temp1[1]
                        if temp2[1] in reads_from.keys():
                            sign_temp=sign_temp+1
                            reads_from[str(temp2[1])+"_"+str(sign_temp)] = temp1[1]
                            reads_from2[str(temp2)]=temp1
                        else:
                            reads_from[str(temp2[1])] = temp1[1]
                            reads_from2[str(temp2)] = temp1

        for i in range(0,len(vlist)):
            sign_temp = 0
            temp3=vlist[i]
            if (i+1)<len(vlist):
                temp4=vlist[i+1]
                if temp3[0]=="W":
                    if temp4[0]=="R" and temp3[1]!=temp4[1]:
                        print "T"+temp4[1]+" reads from T"+temp3[1]
                        if temp4[1] in reads_from.keys():
                            sign_temp=sign_temp+1
                            reads_from[str(temp4[1])+"_"+str(sign_temp)] = temp3[1]
                            reads_from2[str(temp4)] = temp3
                        else:
                            reads_from[str(temp4[1])] = temp3[1]
                            reads_from2[str(temp4)] = temp3

        for i in range(0,len(xlist)):
            sign_temp = 0
            temp5=xlist[i]
            if (i+1)<len(xlist):
                temp6 = xlist[i+1]
                if temp5[0]=="W":
                    if temp6[0]=="R" and temp5[1]!=temp6[1]:
                        print "T"+temp6[1]+" reads from T"+temp5[1]
                        if temp6[1] in reads_from.keys():
                            sign_temp=sign_temp+1
                            reads_from[str(temp6[1])+"_"+str(sign_temp)] = temp5[1]
                            reads_from2[str(temp6)] = temp5
                        else:
                            reads_from[str(temp6[1])] = temp5[1]
                            reads_from2[str(temp6)] = temp5

        for i in range(0, len(ylist)):
            sign_temp = 0
            temp7 = ylist[i]
            if (i+1)<len(ylist):
                temp8 = ylist[i+1]
                if temp7[0] == "W":
                    if temp8[0] == "R" and temp7[1]!=temp8[1]:
                        print "T" + temp8[1] + " reads from T" + temp7[1]
                        if temp8[1] in reads_from.keys():
                            sign_temp=sign_temp+1
                            reads_from[str(temp8[1])+"_"+str(sign_temp)] = temp7[1]
                            reads_from2[str(temp8)] = temp7
                        else:
                            reads_from[str(temp8[1])] = temp7[1]
                            reads_from2[str(temp8)] = temp7

        for i in range(0,len(zlist)):
            sign_temp = 0
            temp9=zlist[i]
            if (i+1)<len(zlist):
                temp10 = zlist[i + 1]
                if temp9[0]=="W":
                    if temp10[0]=="R" and temp9[1]!=temp10[1]:
                        print "T"+temp10[1]+" reads from T"+temp9[1]
                        if temp10[1] in reads_from.keys():
                            sign_temp=sign_temp+1
                            reads_from[str(temp10[1])+"_"+str(sign_temp)] = temp9[1]
                            reads_from2[str(temp10)] = temp9
                        else:
                            reads_from[str(temp10[1])] = temp9[1]
                            reads_from2[str(temp10)] = temp9

        global result
        result = 0
        global result2
        result2 = 0
        global result3
        result3 = 0

        if len(reads_from)==0 :
            result=1
            print"There are no reads from"

        for dep,ini in reads_from.iteritems():
            cdep = ""
            adep = ""
            cini = ""
            aini = ""

            if "C"+dep[0] in oper:
                cdep = oper.index("C" + dep[0])
            if "A"+dep[0] in oper:
                adep = oper.index("A" + dep[0])
            if "C"+ini in oper:
                cini = oper.index("C"+ini)
            if "A"+ini in oper:
                aini = oper.index("A" + ini)


            if adep!="":
                if aini!="":
                    if aini>adep:
                        print"T"+ini+"aborts after T"+dep[0]
                        result=1



            if cini!="":
                if cdep!="":
                    if cdep>cini:
                        print"T"+dep[0]+"commits after T"+ini
                        result=1


            if cini!="":
                if adep!="":
                    if adep>cini:
                        print"T"+dep[0]+"aborts after T"+ini+"commits"
                        result=1

            if cdep!="":
                if cini!="":
                    if cini>cdep:
                        print"T" + ini + "commits after T" + dep[0]
                        result=0
            if aini!="":
                if adep!="":
                    if adep>aini:
                        print"T" + dep[0] + "aborts after T" + ini
                        result=0
            if cini!="":
                if adep!="":
                    if adep<cini:
                        print"T" + dep[0] + "aborts before T" + ini + "commits"
                        result=1
            if cdep!="":
                if aini!="":
                    if aini>cdep:
                        print"T" + ini + "aborts after T" + dep[0] + "commits"
                        result=0
                    if aini<cdep:
                        print"T" + ini + "aborts before T" + dep[0] + "commits"
                        result = 0




        if result==1:
            print "so, Generated History is RC(RECOVERABLE)"
        elif result==0:
            print "so, Generated History is not an RC(RECOVERABLE)"

        print "\n"

        if len(reads_from2)==0 :
            result2=1
            print"There are no reads from"
        for dep1,ini in reads_from2.iteritems():
            dep="R"+dep1[1]+dep1[2]+dep1[3]+dep1[4]
            if dep in b:
                if "C"+ini[1] in b:
                    if b.index(dep)>b.index("C"+ini[1]):
                        print"C"+ini[1]+"comes before "+dep
                        result2=1
                    if b.index(dep)<b.index("C"+ini[1]):
                        print"C" + ini[1] + "comes after " + dep
                        result2=0
                if "A"+ini[1] in b:
                    if b.index(dep)>b.index("A"+ini[1]):
                        print"A"+ini[1]+"comes before "+dep
                        result2=1
                    if b.index(dep)<b.index("A"+ini[1]):
                        print"A" + ini[1] + "comes after " + dep
                        result2=0
            else:
                result2=1
                print"There are no reads by dependent transaction"
        if result2 == 0:
            print "so its not an ACA"
        if result2 == 1:
            print "so its an ACA"

        print "\n"
        if len(reads_from2) == 0:
            result3 = 1
            print"There are no reads from"
        for dep1, ini in reads_from2.iteritems():
            dep = "W" + dep1[1] + dep1[2] + dep1[3] + dep1[4]
            if dep in b:
                if "C" + ini[1] in b:
                    if b.index(dep) > b.index("C" + ini[1]) and b.index(dep1) > b.index("C" + ini[1]):
                        print"C" + ini[1] + "comes before " + dep+"and "+dep1
                        result3 = 1
                    if b.index(dep) < b.index("C" + ini[1]) and b.index(dep1) < b.index("C" + ini[1]):
                        print"C" + ini[1] + "comes after " + dep+"and "+dep1
                        result3 = 0
                if "A" + ini[1] in b:
                    if b.index(dep) > b.index("A" + ini[1]) and b.index(dep1) > b.index("A" + ini[1]):
                        print"A" + ini[1] + "comes before " + dep+"and "+dep1
                        result3 = 1
                    if b.index(dep) < b.index("A" + ini[1]) and b.index(dep1) < b.index("A" + ini[1]):
                        print"A" + ini[1] + "comes after " + dep+"and "+dep1
                        result3 = 0
            else:
                if "C" + ini[1] in b:
                    if  b.index(dep1) > b.index("C" + ini[1]):
                        print"C" + ini[1] + "comes before "+dep1
                        result3 = 1
                    if  b.index(dep1) < b.index("C" + ini[1]):
                        print"C" + ini[1] + "comes after "+dep1
                        result3 = 0
                if "A" + ini[1] in b:
                    if  b.index(dep1) > b.index("A" + ini[1]):
                        print"A " + ini[1] + "comes before " + dep1
                        result3 = 1
                    if  b.index(dep1) < b.index("A" + ini[1]):
                        print"A " + ini[1] + "comes after " +dep1
                        result3 = 0


        if result3 == 0:
            print "so its not an ST(strict history)"
        if result3 == 1:
            print "so its an ST (strict history)"
a=Recover()
a.Recover_check(ordered_history)


perflist=[temp1,temp2,result,result2,result3]

with open("perf.csv", "a") as fp:
    wr = csv.writer(fp)
    wr.writerow(perflist)

tot1=tot2=tot3=tot4=tot5=0

with open("perf.csv") as fin:
    tot1 = tot2 = tot3 = tot4 = tot5 = 0
    for row in csv.reader(fin):
        tot1 += int(row[0])
        tot2 += int(row[1])
        tot3 += int(row[2])
        tot4 += int(row[3])
        tot5 += int(row[4])

objects=['History Serializability','Schedule Serializability','Recoverability','ACA','ST']
values=[tot1,tot2,tot3,tot4,tot5]
y_pos=np.arange(len(objects))

plt.bar(y_pos,values)
plt.xticks(y_pos,objects)
plt.show()