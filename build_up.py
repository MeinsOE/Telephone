from datetime import datetime
import re
from scipy.special import binom
from typing import List
import pickle
import os
from bitarray import bitarray

class Junction:
    isSymmetric:bool = False
    isMonotone:bool = False
    
    def use(a, b):
        pass

class Add(Junction):
    isSymmetric = True
    isMonotone = True
    
    def use(a, b):
        if a+b >= maxNumber:
            return -1
        return a+b

class Multiply(Junction):
    isSymmetric = True
    isMonotone = True

    def use(a, b):
        p = a*b
        if p >= maxNumber:
            return -1
        return p

class Subtract(Junction):
    isSymmetric = True
    isMonotone = False

    def use(a, b):
        return abs(a-b)

class Divide(Junction):
    isSymmetric = True
    isMonotone = False
    
    def use(a, b):
        numerator = max(a, b)
        denominator = min(a, b)
        if denominator==0:
            return -1
        return numerator//denominator

maxPower = 30
maxNumber = 2 ** maxPower
maxStoreNumber = 10**6

class Power(Junction):
    isSymmetric = False
    isMonotone = True
    
    def use(base, exponent):
        if base.bit_length() * exponent > maxPower:
            return -1
        return base**exponent

class Binomial(Junction):
    isSymmetric = True
    isMonotone = False
    
    def use(a, b):
        n = max(a, b)
        k = min(a, b)
        if (max(k, n-k)+1).bit_length() * min(k, n-k) > maxPower:
            return -1
        return int(round(binom(n, k)))



class FindPhoneNumber:
    def __init__(self, targetNumber):
        self.startTime = datetime.now()
        self.numbersFile = "build_up_data/numberBits.pkl"
        self.indicesFile = "build_up_data/indices.pkl"
        self.nodesFileBase = "build_up_data/nodes$$.pkl"
        if os.path.isfile(self.numbersFile):
            with open(self.numbersFile, "rb") as file:
                self.numberBits = pickle.load(file)
            with open(self.indicesFile, "rb") as file:
                self.startingIndices = pickle.load(file)
        else:
            self.numberBits = bitarray(maxNumber)
            for i in range(10):
                self.numberBits[i] = 1
            firstNumberNodes : List[List] = [[number, None, None, "root"] for number in range(1, 10)]
            self.startingIndices = [0, len(firstNumberNodes)]
            self.saveRest(firstNumberNodes, 0, 0)

        self.targetNumber = targetNumber
        self.found = False
        self.funcs : List[Junction] = [Binomial, Power, Divide, Subtract, Multiply, Add]
        if self.numberBits[targetNumber]:
            for i in range(len(self.startingIndices)-1):
                for j in range((self.startingIndices[i+1] - self.startingIndices[i])//maxStoreNumber + 1):
                    nodes = self.getFile(i, j)
                    for node in nodes:
                        if node[0] == targetNumber:
                            print(self.nodeToStr(node))
                            self.found = True
                            break
                    if self.found:
                        break
                if self.found:
                    break
    
    def saveRest(self, nodes, complexity, fileIndex):
        with open(self.nodesFileBase.replace("$$",f"{complexity}-{fileIndex}"), "wb") as file:
            pickle.dump(nodes, file)
        with open(self.numbersFile, "wb") as file:
            pickle.dump(self.numberBits, file)
        with open(self.indicesFile, "wb") as file:
            pickle.dump(self.startingIndices, file)

    def saveFile(self, nodes, complexity, fileIndex):
        with open(self.nodesFileBase.replace("$$",f"{complexity}-{fileIndex}"), "wb") as file:
            pickle.dump(nodes, file)
    
    def nodeToStr(self, node):
        if node[1] is None:
            return f"{node[0]}"
        else:
            return f" {node[0]} = {node[3]}({self.nodeToStr(self.getNode(node[1]))}, {self.nodeToStr(self.getNode(node[2]))}) "

    def getNode(self, index):
        complexityIndex = next(i for i in range(len(self.startingIndices)) if self.startingIndices[i] > index) - 1
        index -= self.startingIndices[complexityIndex]
        fileIndex, nodeIndex = divmod(index, maxStoreNumber)
        nodes = self.getFile(complexityIndex, fileIndex)
        return nodes[nodeIndex]
    
    def getFile(self, complexityIndex, fileIndex):
        with open(self.nodesFileBase.replace("$$",f"{complexityIndex}-{fileIndex}"), "rb") as file:
            return pickle.load(file)


    def scanSymmetricNonMonotoneFunc(self, nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex):
        func = self.funcs[funcIndex]
        returnNodes = []
        for index1 in range(len(nodes1)):
            node1 = nodes1[index1]
            for index2 in range(len(nodes2)):
                if index2 % 100 == 0:
                    self.printStatus(rangeIndex, filesIndex, filesLimit, funcIndex, index1 * len(nodes2) + index2, len(nodes1) * len(nodes2))
                node2 = nodes2[index2]
                result = func.use(node1[0], node2[0])
                if result != -1 and not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1 + indexOffset1, index2 + indexOffset2, func.__name__]
                    if result == self.targetNumber:
                        print(self.nodeToStr(newNode))
                        print()
                        self.found = True
                    returnNodes += [newNode]
        return returnNodes

    def scanSymmetricMonotoneFunc(self, nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex):
        func = self.funcs[funcIndex]
        returnNodes = []
        index1 = 0
        break1 = False
        while not break1 and index1 < len(nodes1):
            node1 = nodes1[index1]
            index2 = 0
            break2 = False
            while not break2 and index2 < len(nodes2):
                if index2 % 100 == 0:
                    self.printStatus(rangeIndex, filesIndex, filesLimit, funcIndex, index1 * len(nodes2) + index2, len(nodes1) * len(nodes2))
                node2 = nodes2[index2]
                result = func.use(node1[0], node2[0])
                if result == -1:
                    break2 = True
                elif not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1 + indexOffset1, index2 + indexOffset2, func.__name__]
                    if result == self.targetNumber:
                        print(self.nodeToStr(newNode))
                        print()
                        self.found = True
                    returnNodes += [newNode]
                index2 += 1
            if index2 == 0:
                break1 = True
            else:
                index1 += 1
        return returnNodes

    def scanAsymmetricNonMonotoneFunc(self, nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex):
        func = self.funcs[funcIndex]
        returnNodes = []
        for index1 in range(len(nodes1)):
            node1 = nodes1[index1]
            for index2 in range(len(nodes2)):
                if index2 % 100 == 0:
                    self.printStatus(rangeIndex, filesIndex, filesLimit, funcIndex, index1 * len(nodes2) + index2, len(nodes1) * len(nodes2))
                node2 = nodes2[index2]
                result = func.use(node1[0], node2[0])
                if result != -1 and not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1 + indexOffset1, index2 + indexOffset2, func.__name__]
                    if result == self.targetNumber:
                        print(self.nodeToStr(newNode))
                        print()
                        self.found = True
                    returnNodes += [newNode]
                result = func.use(node2[0], node1[0])
                if result != -1 and not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index2 + indexOffset2, index1 + indexOffset1, func.__name__]
                    if result == self.targetNumber:
                        print(self.nodeToStr(newNode))
                        print()
                        self.found = True
                    returnNodes += [newNode]
        return returnNodes

    def scanAsymmetricMonotoneFunc(self, nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex):
        func = self.funcs[funcIndex]
        returnNodes = []
        index1 = 0
        break1 = False
        while not break1 and index1 < len(nodes1):
            node1 = nodes1[index1]
            index2 = 0
            break2Order1 = False
            break2Order2 = False
            while not (break2Order1 and break2Order2) and index2 < len(nodes2):
                if index2 % 100 == 0:
                    self.printStatus(rangeIndex, filesIndex, filesLimit, funcIndex, index1 * len(nodes2) + index2, len(nodes1) * len(nodes2))
                node2 = nodes2[index2]
                result = func.use(node1[0], node2[0])
                if result == -1:
                    break2Order1 = True
                elif not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1 + indexOffset1, index2 + indexOffset2, func.__name__]
                    if result == self.targetNumber:
                        print(self.nodeToStr(newNode))
                        print()
                        self.found = True
                    returnNodes += [newNode]
                result = func.use(node2[0], node1[0])
                if result == -1:
                    break2Order2 = True
                elif not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index2 + indexOffset2, index1 + indexOffset1, func.__name__]
                    if result == self.targetNumber:
                        print(self.nodeToStr(newNode))
                        print()
                        self.found = True
                    returnNodes += [newNode]
                index2 += 1
            if index2 == 0:
                break1 = True
            else:
                index1 += 1
        return returnNodes
    
    def addComplexity(self):
        fileIndex = 0
        newStartingIndex = self.startingIndices[-1]
        for rangeIndex in range(len(self.startingIndices)//2):
            otherIndex = len(self.startingIndices) - rangeIndex - 2
            newNodes = []
            limitIndex1 = (self.startingIndices[rangeIndex+1] - self.startingIndices[rangeIndex])//maxStoreNumber + 1
            limitIndex2 = (self.startingIndices[otherIndex+1] - self.startingIndices[otherIndex])//maxStoreNumber + 1
            for fileIndex1 in range(limitIndex1):
                nodes1 = self.getFile(rangeIndex, fileIndex1)
                indexOffset1 = self.startingIndices[rangeIndex] + fileIndex1 * maxStoreNumber
                for fileIndex2 in range(limitIndex2):
                    nodes2 = self.getFile(otherIndex, fileIndex2)
                    indexOffset2 = self.startingIndices[otherIndex] + fileIndex2 * maxStoreNumber
                    filesIndex = fileIndex1 * limitIndex2 + fileIndex2
                    filesLimit = limitIndex1 * limitIndex2
                    for funcIndex, func in enumerate(self.funcs):
                        if func.isSymmetric:
                            if func.isMonotone:
                                newNodes += self.scanSymmetricMonotoneFunc(nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex)
                            else:
                                newNodes += self.scanSymmetricNonMonotoneFunc(nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex)
                        else:
                            if func.isMonotone:
                                newNodes += self.scanAsymmetricMonotoneFunc(nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex)
                            else:
                                newNodes += self.scanAsymmetricNonMonotoneFunc(nodes1, nodes2, indexOffset1, indexOffset2, rangeIndex, filesIndex, filesLimit, funcIndex)
                        while len(newNodes) >= maxStoreNumber:
                            toSave = newNodes[:maxStoreNumber]
                            newNodes = newNodes[maxStoreNumber:]
                            self.saveFile(sorted(toSave), len(self.startingIndices)-1, fileIndex)
                            fileIndex += 1
                            newStartingIndex += maxStoreNumber
        newStartingIndex += len(newNodes)
        self.startingIndices += [newStartingIndex]
        self.saveRest(sorted(newNodes), len(self.startingIndices)-2, fileIndex) # since the next index is already added
        print(datetime.now() - self.startTime)
        print()
    
    def printStatus(self, rangeIndex, filesIndex, filesLimit, funcIndex, pairIndex, pairLimit):
        spacing = "                    "
        print(f"Complexity={len(self.startingIndices)} ({self.startingIndices[-1]}){spacing}")
        print(f"Group {rangeIndex+1} / {len(self.startingIndices)//2}{spacing}")
        print(f"Combs {filesIndex+1} / {filesLimit}{spacing}")
        print(f"Func {funcIndex+1} / {len(self.funcs)}{spacing}")
        print(f"Pair {pairIndex+1} / {pairLimit}{spacing}")
        print("\033[A\033[A\033[A\033[A\033[A", end="")


if __name__ == "__main__":
    findPhoneNumber = FindPhoneNumber(9851722)
    while not findPhoneNumber.found:
        findPhoneNumber.addComplexity()