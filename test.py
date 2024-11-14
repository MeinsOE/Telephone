import timeit

maxPower = 30
maxNumber = 2**maxPower
stepSize = maxNumber//10000

def loop(func):
    for a in range(-maxNumber, maxNumber, stepSize):
        func(max(a, -1))

def optionA(a):
    return a > 0

def optionB(a):
    return a != -1

# Measure time
print("Option A:", timeit.timeit("loop(optionA)", globals=globals(), number=1000))
print("Option B:", timeit.timeit("loop(optionB)", globals=globals(), number=1000))
