import csv

filename = "runtime_logs/java.csv"
values = []

with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Skip lines that don't start with the expected prefix
        if not row or not row[0].startswith("pmd_optimized"):
            continue
        # Convert all columns except the first to float
        values.append([float(x) for x in row[1:]])

# Transpose to get columns
columns = list(zip(*values))
means = [sum(col)/len(col) for col in columns]

print("Means for each column:")
for i, mean in enumerate(means, start=2):
    print(f"Column {i}: {mean}")