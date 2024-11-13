import pickle
from build_up import NumberNode

numberNodes = [NumberNode.root(number) for number in range(10)]

with open("pickle_test.pkl", "wb") as file:
    pickle.dump(numberNodes, file)
    
with open("pickle_test.pkl", "rb") as file:
    test = pickle.load(file)

print([str(t) for t in test])