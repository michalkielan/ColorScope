import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import random 

x = [random.randint(0, 255) for p in range(0, 1000)]

sns.distplot(x)
plt.show()
