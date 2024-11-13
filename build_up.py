from datetime import datetime
from scipy.special import binom
from typing import List
import pickle
import os
from bitarray import bitarray

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
    isSymmetric = True

    def use(a, b):
        return abs(a-b)

class Divide(Junction):
    isSymmetric = True
    
    def use(a, b):
        numerator = max(a, b)
        denominator = min(a, b)
        if denominator==0:
            return 1 # always already satisfied
        return numerator//denominator

maxPower = 30
maxNumber = 2 ** maxPower

class Power(Junction):
    isSymmetric = False
    
    def use(base, exponent):
        if base.bit_length() * exponent > maxPower:
            return 1 # always already satisfied
        return base**exponent

class Binomial(Junction):
    isSymmetric = True
    
    def use(a, b):
        n = max(a, b)
        k = min(a, b)
        if max(k, n-k).bit_length() * min(k, n-k) > maxPower:
            return 1 # always already satisfied
        return int(round(binom(n, k)))
    
def nodeToStr(node):
    if node[1] is None:
        return f"{node[0]}"
    else:
        return f" {node[0]} = {node[3]}({nodeToStr(numberNodes[node[1]])}, {nodeToStr(numberNodes[node[2]])}) "

funcs = [Binomial, Power, Divide, Subtract, Multiply, Add]

if __name__ == "__main__":
    startTime = datetime.now()
    numbersFile = "build_up_data/numberBits.pkl"
    nodesFile = "build_up_data/nodes.pkl"
    indicesFile = "build_up_data/indices.pkl"
    if os.path.isfile(numbersFile):
        with open(numbersFile, "rb") as file:
            numberBits = pickle.load(file)
        with open(indicesFile, "rb") as file:
            startingIndices = pickle.load(file)
        with open(nodesFile, "rb") as file:
            numberNodes = pickle.load(file)
    else:
        numberBits = bitarray(maxNumber)
        for i in range(10):
            numberBits[i] = 1
        numberNodes : List[List] = [[number, None, None, "root"] for number in range(1, 10)]
        startingIndices = [0]

    targetNumber = 9851722
    found = False
    if numberBits[targetNumber]:
        for node in numberNodes:
            if node[0] == targetNumber:
                print(node)
                found = True
    while not found:
        startingIndices += [len(numberNodes)]
        print(f"complexity={len(startingIndices)}")
        print(f"{startingIndices[-1]}")
        print(len(startingIndices)//2)
        print()
        for rangeIndex in range(len(startingIndices)//2):
            for index1 in range(startingIndices[rangeIndex], startingIndices[rangeIndex+1]):
                node1 = numberNodes[index1]
                print (f"\033[A{rangeIndex+1}: {index1 - startingIndices[rangeIndex] + 1} / {startingIndices[rangeIndex+1] - startingIndices[rangeIndex]}")
                for index2 in range(startingIndices[-rangeIndex-2], startingIndices[-rangeIndex-1]):
                    node2 = numberNodes[index2]
                    for func in funcs:
                        if func.isSymmetric:
                            result = func.use(node1[0], node2[0])
                            if result < maxNumber and  not numberBits[result]:
                                numberBits[result] = 1
                                newNode = [result, index1, index2, func.__name__]
                                if result == targetNumber:
                                    print(newNode)
                                    print()
                                    found = True
                                numberNodes += [newNode]
                        else:
                            result = func.use(node1[0], node2[0])
                            if result < maxNumber and  not numberBits[result]:
                                numberBits[result] = 1
                                newNode = [result, index1, index2, func.__name__]
                                if result == targetNumber:
                                    print(newNode)
                                    print()
                                    found = True
                                numberNodes += [newNode]
                            result = func.use(node2[0], node1[0])
                            if result < maxNumber and  not numberBits[result]:
                                numberBits[result] = 1
                                newNode = [result, index2, index1, func.__name__]
                                if result == targetNumber:
                                    print(newNode)
                                    print()
                                    found = True
                                numberNodes += [newNode]
        with open(numbersFile, "wb") as file:
            pickle.dump(numberBits, file)
        with open(nodesFile, "wb") as file:
            pickle.dump(numberNodes, file)
        with open(indicesFile, "wb") as file:
            pickle.dump(startingIndices, file)
        print(datetime.now() - startTime)