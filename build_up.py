from scipy.special import binom
from typing import List
import pickle
import os

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
        if base.bit_length() * exponent > maxPowerValue:
            return 1 # always already satisfied
        return base**exponent

class Binomial(Junction):
    isSymmetric = False
    
    def use(n, k):
        if k>n or max(k, n-k).bit_length() * min(k, n-k) > maxPowerValue:
            return 1 # always already satisfied
        return int(round(binom(n, k)))

class NumberNode:
    def __init__(self, number:int, childIndex1:int, childIndex2:int, method:str):
        self.number = number
        self.childIndex1 = childIndex1
        self.childIndex2 = childIndex2
        self.method=method

    @classmethod        
    def root(cls, number:int):
        return cls(number, None, None, "root")
    
    def __str__(self):
        if self.childIndex1 is None:
            return f"{self.number}"
        else:
            return f" {self.number} = {self.method}({numberNodes[self.childIndex1].__str__()}, {numberNodes[self.childIndex2].__str__()}) "

funcs = [Binomial, Power, Divide, Subtract, Multiply, Add]

if __name__ == "__main__":
    numbersFile = "build_up_data/numbers.pkl"
    nodesFile = "build_up_data/nodes.pkl"
    indicesFile = "build_up_data/indices.pkl"
    if os.path.isfile(numbersFile):
        with open(numbersFile, "rb") as file:
            numbers = pickle.load(file)
        with open(indicesFile, "rb") as file:
            startingIndices = pickle.load(file)
        with open(nodesFile, "rb") as file:
            numberNodes = pickle.load(file)
    else:
        numbers = set([i for i in range(1, 10)])
        numberNodes : List[NumberNode] = [NumberNode.root(number) for number in numbers]
        startingIndices = [0]

    targetNumber = 31445304
    found = False
    if targetNumber in numbers:
        for node in numberNodes:
            if node.number == targetNumber:
                print(node)
                found = True
    while not found:
        startingIndices += [len(numberNodes)]
        print(f"complexity={len(startingIndices)}")
        print(f"{startingIndices[-1]}")
        print(int(len(startingIndices)/2))
        print()
        for rangeIndex in range(int(len(startingIndices)/2)):
            for index1 in range(startingIndices[rangeIndex], startingIndices[rangeIndex+1]):
                node1 = numberNodes[index1]
                print (f"\033[A{rangeIndex+1}: {index1 - startingIndices[rangeIndex] + 1} / {startingIndices[rangeIndex+1] - startingIndices[rangeIndex]}")
                for index2 in range(startingIndices[-rangeIndex-2], startingIndices[-rangeIndex-1]):
                    node2 = numberNodes[index2]
                    for func in funcs:
                        if func.isSymmetric:
                            result = func.use(node1.number, node2.number)
                            if result not in numbers:
                                numbers.add(result)
                                newNode = NumberNode(result, index1, index2, func.__name__)
                                if result == targetNumber:
                                    print(newNode)
                                    print()
                                    found = True
                                numberNodes += [newNode]
                        else:
                            result = func.use(node1.number, node2.number)
                            if result not in numbers:
                                numbers.add(result)
                                newNode = NumberNode(result, index1, index2, func.__name__)
                                if result == targetNumber:
                                    print(newNode)
                                    print()
                                    found = True
                                numberNodes += [newNode]
                            result = func.use(node2.number, node1.number)
                            if result not in numbers:
                                numbers.add(result)
                                newNode = NumberNode(result, index2, index1, func.__name__)
                                if result == targetNumber:
                                    print(newNode)
                                    print()
                                    found = True
                                numberNodes += [newNode]
        with open(numbersFile, "wb") as file:
            pickle.dump(numbers, file)
        with open(nodesFile, "wb") as file:
            pickle.dump(numberNodes, file)
        with open(indicesFile, "wb") as file:
            pickle.dump(startingIndices, file)