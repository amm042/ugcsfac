import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from collections import OrderedDict
from matplotlib import cm
import numpy as np
df = pd.read_csv('pubs.csv')

#print(df.university.unique())

#print(df)
fig, ax = plt.subplots(1,1,figsize=(10,7))

x = list(range(2009, 2020))
univs = df.university.unique()

cm = plt.cm.get_cmap('tab20')

print(len(univs))
for i,univ in enumerate(sorted(univs)):

    y = [len(df[np.logical_and(
                df.university==univ,
                df.year==year)]) for year in x]
    ax.plot(x,y,label=univ,alpha=0.95,
            lw=5 if univ=='bucknell' else 2,
            color=cm(i/len(univs)))

ax.xaxis.set_major_locator(MultipleLocator(1))
ax.set_ylabel('dblp count')
ax.set_xlabel('year')
ax.set_ylim(bottom=0)
ax.legend()
plt.tight_layout()

plt.show()
