import timeit

maxPower = 30
maxNumber = 2**maxPower
stepSize = maxNumber//100

def loop(func):
    for a in range(0, maxNumber, stepSize):
        for b in range(0, maxNumber, stepSize):
            func(a, b)

def withoutBitLength(a, b):
    p = a**b
    if p > maxNumber:
        return 1
    return p

def withBitLength(a, b):
    if a.bit_length() * b > maxPower:
        return 1
    return a**b

# Measure time
print("Time with bit_length variable:", timeit.timeit("loop(withBitLength)", globals=globals(), number=1))
print("Time without bit_length variable:", timeit.timeit("loop(withoutBitLength)", globals=globals(), number=1))
