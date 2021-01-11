from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json

d = {'col1': [1, 2, 3], 'col2': [3, 4, 5]}
df = pd.DataFrame(data=d)
df = df.set_axis(['a', 'b', 'a'], axis='index')
print(df.loc['a'])