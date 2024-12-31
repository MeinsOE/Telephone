import os
import pickle
import re
from collections import defaultdict
import shutil

# Directory containing your files
directory = 'build_up_data'
newDirectory = "build_up_data_new"
filePattern = "nodes7-$.pkl"

# Regex pattern to extract the first and second integers
pattern = re.compile(r'nodes7-(\d+)\.pkl')

newIndices = [0]

total = 0

# Process files
for file_name in os.listdir(directory):
    match = pattern.match(file_name)
    if match:
        first, = map(int, match.groups())
        shutil.copy(os.path.join(directory, file_name), os.path.join(newDirectory, filePattern.replace("$", f"{first-1}")))
    else:
        shutil.copy(os.path.join(directory, file_name), newDirectory)