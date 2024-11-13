import numpy as np
from scipy.special import binom
from typing import List
import pickle
import os
from enum import Enum

class Junction:
    isSymmetric:bool = False
    
    def use(a, b):
        pass

class Add(Junction):
    isSymmetric = True
    
    def use(a, b):
        return a+b

class Multiply(Junction):
    isSymmetric = True

    def use(a, b):
        return a*b

class Subtract(Junction):
    isSymmetric = False

    def use(a, b):
        if b>a:
            return 1 # always already satisfied
        return a-b

class Divide(Junction):
    isSymmetric = False
    
    def use(numerator, denominator):
        if denominator==0:
            return 1 # always already satisfied
        return int(numerator/denominator)

maxPowerValue = 30

class Power(Junction):
    isSymmetric = False
    
    def use(base, exponent):
        if int(base).bit_length() * exponent > maxPowerValue:
            return 1 # always already satisfied
        return base**exponent

class Binomial(Junction):
    isSymmetric = False
    
    def use(n, k):
        if k>n or int(max(k, n-k)).bit_length() * min(k, n-k) > maxPowerValue:
            return 1 # always already satisfied
        return int(round(binom(n, k)))

class NumberGraph:
    def __init__(self, numberNodes, funcs, indices=None, dtype=np.uint64):
        self.numberNodes = np.array(numberNodes, dtype=dtype)
        self.funcs = funcs
        if indices is None:
            indices = [0, len(numberNodes)]
        self.indices = np.array(indices, dtype=dtype)
        self.dtype=dtype

    def print(self, index):
        numberNode = self.numberNodes[index]
        if numberNode[Column.FUNC] == len(self.funcs):
            print(f"{numberNode[Column.NUMBER]}")
        else:
            print(f" {numberNode[Column.NUMBER]} = {numberNode[Column.FUNC]}({self.print(numberNode[Column.CHILD1])}, {self.print(numberNode[Column.CHILD2])}) ")

    def indexOf(self, number:int) -> int:
        for i in range(len(self.indices)-1):
            if number <= self.numberNodes[self.indices[i+1]-1, Column.NUMBER]:
                index = self.binarySearch(number, self.indices[i], self.indices[i+1])
                if index != -1:
                    return index
        return -1

    def binarySearch(self, number:int, lower:int, upper:int) -> int:
        if upper-lower <= 1:
            if self.numberNodes[lower, Column.NUMBER] == number:
                return lower
            return -1
        middle = (upper+lower)//2
        if self.numberNodes[middle, Column.NUMBER] == number:
            return middle
        if number < self.numberNodes[middle, Column.NUMBER]:
            return self.binarySearch(number, lower, middle)
        else:
            return self.binarySearch(number, middle+1, upper)
    
    def searchAndPrint(self, number:int) -> int:
        index = self.indexOf(number)
        if index != -1:
            self.print(index)
        return index
    
    def addComplexity(self, target) -> bool:
        found = False
        self.newNodes = []
        for rangeIndex in range(int(len(self.indices)/2)):
            for index1 in range(self.indices[rangeIndex], self.indices[rangeIndex+1]):
                print (f"\033[A{rangeIndex+1}: {index1 - self.indices[rangeIndex] + 1} / {self.indices[rangeIndex+1] - self.indices[rangeIndex]}")
                for index2 in range(self.indices[-rangeIndex-2], self.indices[-rangeIndex-1]):
                    for funcIndex, func in enumerate(self.funcs):
                        if func.isSymmetric:
                            self.checkFunc(target, index1, index2, funcIndex, func)
                        else:
                            self.checkFunc(target, index1, index2, funcIndex, func)
                            self.checkFunc(target, index2, index1, funcIndex, func)
        self.addNewNodes()
        return found

    def checkFunc(self, targetNumber, index1, index2, funcIndex, func):
        result = func.use(self.numberNodes[index1][Column.NUMBER], self.numberNodes[index2][Column.NUMBER])
        newNode = [result, index1, index2, funcIndex]
        if self.indexOf(result) == -1:
            index = self.insertNewNode(newNode)
            if index != -1 and result == targetNumber:
                self.print(index)
                print()
    
    def insertNewNode(self, newNode) -> int:
        if len(self.newNodes) == 0:
            self.newNodes = [newNode]
            return 0
        if newNode[Column.NUMBER] < self.newNodes[0][Column.NUMBER] :
            self.newNodes = [newNode] + self.newNodes
            return 0
        if newNode[Column.NUMBER] > self.newNodes[-1][Column.NUMBER]:
            self.newNodes += [newNode]
            return len(self.newNodes)-1
        return self.insertBinary(newNode, 0, len(self.newNodes))
    
    def insertBinary(self, newNode, lower:int, upper:int) -> int:
        if lower == upper-1:
            if self.newNodes[lower][Column.NUMBER] == newNode[Column.NUMBER]:
                return -1
            self.newNodes.insert(lower + 1, newNode)
            return lower + 1
        middle = (upper+lower)//2
        if newNode[Column.NUMBER] < self.newNodes[middle][Column.NUMBER]:
            return self.insertBinary(newNode, lower, middle)
        else:
            return self.insertBinary(newNode, middle, upper)
        
    def addNewNodes(self):
        self.numberNodes = np.concatenate((self.numberNodes, np.array(self.newNodes, dtype=self.dtype)), dtype=self.dtype)
        self.indices = np.concatenate((self.indices, np.array([len(self.numberNodes)], dtype=self.dtype)), dtype=self.dtype)
    
    def save(self, dirPath:str):
        np.save(os.path.join(dirPath, "nodes.npy"), self.numberNodes)
        np.save(os.path.join(dirPath, "indices.npy"), self.indices)

    def tryLoad(self, dirPath:str):
        if os.path.isfile(os.path.join(dirPath, "nodes.npy")):
            self.numberNodes = np.load(os.path.join(dirPath, "nodes.npy"))
            self.dtype=self.numberNodes.dtype
            self.indices = np.load(os.path.join(dirPath, "indices.npy"))

class Column():
    NUMBER = 0
    CHILD1 = 1
    CHILD2 = 2
    FUNC = 3

funcs = [Binomial, Power, Divide, Subtract, Multiply, Add]

if __name__ == "__main__":
    numberGraph = NumberGraph([[number, 0, 0, len(funcs)] for number in range(0, 10)], funcs)
    dirPath = "build_up_data"
    numberGraph.tryLoad(dirPath)

    target = 31445304
    found = numberGraph.searchAndPrint(target) != -1
    while not found:
        print(f"complexity={len(numberGraph.indices)}")
        print(f"{numberGraph.indices[-1]}")
        print()
        numberGraph.addComplexity(target)
        numberGraph.save(dirPath)