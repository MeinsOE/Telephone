
import pickle


with open("build_up_data/numberBits.pkl", "rb") as file:
    numberBits = pickle.load(file)

for number in range(10**8):
    if numberBits[number] == 0:
        print(number)