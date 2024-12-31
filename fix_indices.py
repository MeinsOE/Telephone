import os
import pickle
import re
from collections import defaultdict

# Directory containing your files
directory = 'build_up_data'

# Regex pattern to extract the first and second integers
pattern = re.compile(r'nodes(\d+)-(\d+)\.pkl')

newIndices = [0]

total = 0

# Process files
for file_name in os.listdir(directory):
    match = pattern.match(file_name)
    if match:
        first, second = map(int, match.groups())
        diff = first - len(newIndices) + 2
        if diff > 0:
            newIndices += [0] * diff
        
        with open(os.path.join(directory, file_name), "rb") as file:
            length = len(pickle.load(file))
            if length != 10**6:
                print(f"{first}\t{second}\t{length}")
            newIndices[first+1] += length
            total += length
for i in range(len(newIndices) - 1):
    newIndices[i+1] +=newIndices[i]
print(newIndices)

with open("build_up_data\indices.pkl", "wb") as file:
    pickle.dump([0, 9, 81, 1524, 3867, 104848, 1565427, 20611220, 184988445, 642200127], file)