from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import requests
import os

today=datetime.date.today()
formatted_today=today.strftime('%y%m%d')
yesterday=int(formatted_today)-1
date='20'+str(yesterday)

html = urlopen('https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cdas.'+date+'/')
bsObj = BeautifulSoup(html, 'html.parser')
t1 = bsObj.find_all('a')

curpath = os.path.abspath(os.curdir)
print(curpath)

count = 1
for t2 in t1:
   t3 = t2.get('href')

   if ('sflux' in t3) and ('idx' not in t3) and (count <= 7):

       if count == 1:
           count += 1
           continue
       url='https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cdas.'+date+'/'+t3
       print(url)

       r = requests.get(url)
       with open(curpath+'/temperature_data/'+t3+'.txt', 'wb') as f:
           f.write(r.content)
       count += 1