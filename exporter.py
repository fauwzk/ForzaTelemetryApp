import csv

def writefile():
    i = 0
    with open('test.csv', 'w') as f:
        writer = csv.writer(f)
        while i < 10:
            writer.writerow("test")
        i += 1