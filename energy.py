import numpy as np
import matplotlib.pyplot as plt

#data = np.fromfile("..\\2677\\0001.pel",np.uint64)
data = np.fromfile("..\\3671\\test.pel",np.uint64)
#data = np.fromfile("..\\1565\\test_('7', '7', '0', '0').pel",np.uint64)

data = ((data[32:] >> 22) & 0x1FF)

#print(np.min(data))
print(np.mean(data))
print(np.std(data))
print(np.std(data)/np.mean(data))

data2 = np.fromfile("..\\3669\\0001.pel",np.uint64) 
data2 = ((data2[32:] >> 22) & 0x1FF) 

plt.hist(data2,range(0,512,8),log=True)
plt.hist(data,range(0,512,8),log=True)
plt.show()

