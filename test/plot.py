import matplotlib.pyplot as plt
import csv

list = []
list2 = []
list3 = []
list4 = []
list5 = []
list6 = []

with open('data.csv', 'r') as f:
    reader = csv.reader(f)

    for row in reader:
       list.append(row[0]) 
       list2.append(row[1]) 
       list3.append(row[2]) 
       list4.append(row[3]) 
       list5.append(row[4]) 
       list6.append(row[5]) 

plt.plot(list,color="red")
plt.plot(list2,color="green")
plt.plot(list3,color="blue")
plt.plot(list4,color="yellow")
plt.plot(list5,color="black")
plt.plot(list6,color="cyan")

plt.show()
