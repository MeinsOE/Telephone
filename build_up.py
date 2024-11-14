from datetime import datetime
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
        self.nodesFile = "build_up_data/nodes.pkl"
        self.indicesFile = "build_up_data/indices.pkl"
        if os.path.isfile(self.numbersFile):
            with open(self.numbersFile, "rb") as file:
                self.numberBits = pickle.load(file)
            with open(self.indicesFile, "rb") as file:
                self.startingIndices = pickle.load(file)
            with open(self.nodesFile, "rb") as file:
                self.numberNodes = pickle.load(file)
        else:
            self.numberBits = bitarray(maxNumber)
            for i in range(10):
                self.numberBits[i] = 1
            self.numberNodes : List[List] = [[number, None, None, "root"] for number in range(1, 10)]
            self.startingIndices = [0]

        self.targetNumber = targetNumber
        self.found = False
        self.funcs : List[Junction] = [Binomial, Power, Divide, Subtract, Multiply, Add]
        if self.numberBits[targetNumber]:
            for node in self.numberNodes:
                if node[0] == targetNumber:
                    print(node)
                    self.found = True
    
    def nodeToStr(self, node):
        if node[1] is None:
            return f"{node[0]}"
        else:
            return f" {node[0]} = {node[3]}({self.nodeToStr(self.numberNodes[node[1]])}, {self.nodeToStr(self.numberNodes[node[2]])}) "

    def scanSymmetricNonMonotoneFunc(self, rangeIndex, func):
        for index1 in range(self.startingIndices[rangeIndex], self.startingIndices[rangeIndex+1]):
            node1 = self.numberNodes[index1]
            print (f"\033[A {index1 - self.startingIndices[rangeIndex] + 1} / {self.startingIndices[rangeIndex+1] - self.startingIndices[rangeIndex]}")
            for index2 in range(self.startingIndices[-rangeIndex-2], self.startingIndices[-rangeIndex-1]):
                node2 = self.numberNodes[index2]
                result = func.use(node1[0], node2[0])
                if result != -1 and not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1, index2, func.__name__]
                    if result == self.targetNumber:
                        print(newNode)
                        print()
                        self.found = True
                    self.numberNodes += [newNode]

    def scanSymmetricMonotoneFunc(self, rangeIndex, func):
        index1 = self.startingIndices[rangeIndex]
        break1 = False
        while not break1 and index1 < self.startingIndices[rangeIndex+1]:
            node1 = self.numberNodes[index1]
            print (f"\033[A {index1 - self.startingIndices[rangeIndex] + 1} / {self.startingIndices[rangeIndex+1] - self.startingIndices[rangeIndex]}")
            index2 = self.startingIndices[-rangeIndex-2]
            break2 = False
            while not break2 and index2 < self.startingIndices[-rangeIndex-1]:
                node2 = self.numberNodes[index2]
                result = func.use(node1[0], node2[0])
                if result == -1:
                    break2 = True
                elif not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1, index2, func.__name__]
                    if result == self.targetNumber:
                        print(newNode)
                        print()
                        self.found = True
                    self.numberNodes += [newNode]
                index2 += 1
            if index2 == self.startingIndices[-rangeIndex-2]:
                break1 = True
            else:
                index1 += 1

    def scanAsymmetricNonMonotoneFunc(self, rangeIndex, func):
        for index1 in range(self.startingIndices[rangeIndex], self.startingIndices[rangeIndex+1]):
            node1 = self.numberNodes[index1]
            print (f"\033[A {index1 - self.startingIndices[rangeIndex] + 1} / {self.startingIndices[rangeIndex+1] - self.startingIndices[rangeIndex]}")
            for index2 in range(self.startingIndices[-rangeIndex-2], self.startingIndices[-rangeIndex-1]):
                node2 = self.numberNodes[index2]
                result = func.use(node1[0], node2[0])
                if result != -1 and not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1, index2, func.__name__]
                    if result == self.targetNumber:
                        print(newNode)
                        print()
                        self.found = True
                    self.numberNodes += [newNode]
                result = func.use(node2[0], node1[0])
                if result != -1 and not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index2, index1, func.__name__]
                    if result == self.targetNumber:
                        print(newNode)
                        print()
                        self.found = True
                    self.numberNodes += [newNode]

    def scanAsymmetricMonotoneFunc(self, rangeIndex, func):
        index1 = self.startingIndices[rangeIndex]
        break1 = False
        while not break1 and index1 < self.startingIndices[rangeIndex+1]:
            node1 = self.numberNodes[index1]
            print (f"\033[A {index1 - self.startingIndices[rangeIndex] + 1} / {self.startingIndices[rangeIndex+1] - self.startingIndices[rangeIndex]}")
            index2 = self.startingIndices[-rangeIndex-2]
            break2Order1 = False
            break2Order2 = False
            while not (break2Order1 and break2Order2) and index2 < self.startingIndices[-rangeIndex-1]:
                node2 = self.numberNodes[index2]
                result = func.use(node1[0], node2[0])
                if result == -1:
                    break2Order1 = True
                elif not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index1, index2, func.__name__]
                    if result == self.targetNumber:
                        print(newNode)
                        print()
                        self.found = True
                    self.numberNodes += [newNode]
                result = func.use(node2[0], node1[0])
                if result == -1:
                    break2Order2 = True
                elif not self.numberBits[result]:
                    self.numberBits[result] = 1
                    newNode = [result, index2, index1, func.__name__]
                    if result == self.targetNumber:
                        print(newNode)
                        print()
                        self.found = True
                    self.numberNodes += [newNode]
                index2 += 1
            if index2 == self.startingIndices[-rangeIndex-2]:
                break1 = True
            else:
                index1 += 1
    
    def addComplexity(self):
        self.startingIndices += [len(self.numberNodes)]
        print(f"complexity={len(self.startingIndices)}")
        print(f"{self.startingIndices[-1]}")
        print()
        print()
        print()
        for rangeIndex in range(len(self.startingIndices)//2):
            print(f"\033[A\033[A\033[AGroup {rangeIndex+1}")
            print()
            print()
            for i, func in enumerate(self.funcs):
                print(f"\033[A\033[AFunc {i+1} / {len(self.funcs)}")
                print()
                if func.isSymmetric:
                    if func.isMonotone:
                        self.scanSymmetricMonotoneFunc(rangeIndex, func)
                    else:
                        self.scanSymmetricNonMonotoneFunc(rangeIndex, func)
                else:
                    if func.isMonotone:
                        self.scanAsymmetricMonotoneFunc(rangeIndex, func)
                    else:
                        self.scanAsymmetricNonMonotoneFunc(rangeIndex, func)
        self.numberNodes[self.startingIndices[-1]:] = sorted(self.numberNodes[self.startingIndices[-1]:], key=lambda node: node[0])
        with open(self.numbersFile, "wb") as file:
            pickle.dump(self.numberBits, file)
        with open(self.nodesFile, "wb") as file:
            pickle.dump(self.numberNodes, file)
        with open(self.indicesFile, "wb") as file:
            pickle.dump(self.startingIndices, file)
        print(datetime.now() - self.startTime)

if __name__ == "__main__":
    findPhoneNumber = FindPhoneNumber(9851722)
    while not findPhoneNumber.found:
        findPhoneNumber.addComplexity()