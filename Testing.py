import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

x = np.array([1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9])
y = np.array([13, 14, 17, 12, 23, 24, 25, 25, 24, 28, 32, 33])

plt.plot(x,y, 'o')
r = np.corrcoef(x, y)
m, b = np.polyfit(x, y, 1)
print(m, 'x +', b)
plt.plot(x, m*x + b)
plt.show()

