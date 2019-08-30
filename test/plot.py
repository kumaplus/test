import matplotlib.pyplot as plt
import csv

list = []
list2 = []

with open('data.csv', 'r') as f:
    reader = csv.reader(f)

    for row in reader:
       list.append(row[0]) 
       list2.append(row[1]) 

plt.plot(list,color="red")
plt.plot(list2,color="green")

plt.show()
