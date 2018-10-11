# -*- coding:utf-8 _*-  
__author__ = 'luyue'
__date__ = '2018/5/1 16:24'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pandas import Series,DataFrame
from numpy.random import randn
import numpy as np
import matplotlib.pyplot as plt

loandata = pd.DataFrame(pd.read_csv('D:/bask.csv', encoding='gb2312'))
names = list(loandata['球员'])
# test = pd.DataFrame(loandata['场均得分'])
# test.plot(kind='bar')

df = pd.DataFrame(list(loandata['三分%']), index=names, columns=['Three-point shooting'])
df.plot(kind='bar')
plt.show()
plt.show()