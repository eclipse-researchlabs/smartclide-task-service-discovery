# -*- coding: utf-8 -*-
"""FRAMEWORK_programmableweb.ipynb

#https://www.programmableweb.com/category/all/web-development-frameworks?page=0

!pip install requests-random-user-agent
!pip install pandas
!pip install bs4
!pip install lxml

"""
import multiprocessing
multiprocessing.cpu_count()

import requests
import requests_random_user_agent
#s = requests.Session()
#print(s.headers['User-Agent'])

# Without a session
resp = requests.get('https://httpbin.org/user-agent')
print(resp.json()['user-agent'])

import concurrent.futures
import requests
import requests_random_user_agent
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

def _download_FRAME(url):

  df_tempSDK = pd.DataFrame()

  rq = requests.get(url)
  
  if rq.status_code == 404 or rq.status_code == 403: ## Handle more error codes...
    exit

  main_data = rq.text

  # dataset from table
  df_tempSDK = pd.read_html(main_data, index_col=0)[0]

  main_soup = BeautifulSoup(main_data, 'html.parser')
  
  main_names = main_soup.find_all('tr')[1:245]

  list_urlSDK = []

  # Head url for meta_url
  head_Url= 'https://www.programmableweb.com'

  for row in main_names:
       text = row.find_all('td')[0]      
       list_urlSDK.append( (head_Url + str(text).partition('<a href="')[2].partition('">')[0])) # Meta URL 


  df_tempSDK['Meta_Url'] = list_urlSDK

  return df_tempSDK


def download_FRAME(bulk_urls, num_Splits):
  df_temp = pd.DataFrame()

  # Split urls
  urls_splited  = np.array_split(bulk_urls, num_Splits) # max workers

  tasks = []

  for split in range(len(urls_splited)):
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(urls_splited)) as executor:
      for url in urls_splited[split]:    
        tasks.append(executor.submit(_download_FRAME, url))
       ## mb call with bulk urls instead of one by one
  # Union
  for result in tasks:
    df_temp = df_temp.append(result.result())

  return df_temp

FRAME_urls=[]
for i in range(23): ## web pages?.. 22+1
    main_url = 'https://www.programmableweb.com/category/all/web-development-frameworks?page=' + str(i)
    FRAME_urls.append(main_url)

#SDK_urls
df_FRAME = pd.DataFrame()
df_FRAME = download_FRAME(FRAME_urls, 5) # Num workers
#df_SDK.drop('Published', inplace=True, axis=1)
df_FRAME

# Creates new columns
df_FRAME['Languages'] = ""
df_FRAME['Provider'] = ""
df_FRAME['Asset URL'] = ""
df_FRAME['Repository'] = ""
df_FRAME['Terms Of Service'] = ""

def _download_meta_url(df_source):

  for i in range(len(df_source)):

    #print(df_source)
    meta_url = df_source['Meta_Url'][i]
    rq = requests.get(meta_url)

    if rq.status_code == 404 or rq.status_code == 403: ## Handle more error codes...
      continue

    meta_data = rq.text
    meta_soup = BeautifulSoup(meta_data, 'html.parser')

    # Update Description from the meta url
    meta_description = str(meta_soup.find('div', class_='tabs-header_description')).partition('">')[2].partition('</')[0]
    
    df_source['Description'][i] = meta_description 

    meta_specs = meta_soup.find('div', class_='section specs')

    for lab in meta_specs.select("label"):   

      # Search for Languages
      if (lab.text.lower().find("languages") > -1):
          #print(lab.text + ": " + lab.find_next_sibling().text)
          df_source['Languages'][i] =   lab.find_next_sibling().text

      # Search for Provider
      if (lab.text.lower().find("provider") > -1):
          #print(lab.text + ": " + lab.find_next_sibling().text)
          df_source['Provider'][i] =   lab.find_next_sibling().text

      # Search for URL
      if (lab.text.lower().find("asset home") > -1):
         #print(lab.text + ": " + lab.find_next_sibling().text)
          df_source['Asset URL'][i] =   lab.find_next_sibling().text

      # Search for Repo
      if (lab.text.lower().find("repository") > -1):
          #print(lab.text + ": " + lab.find_next_sibling().text)
          df_source['Repository'][i] =   lab.find_next_sibling().text

      # Search for Provider
      if (lab.text.lower().find("terms of service") > -1):
         #print(lab.text + ": " + lab.find_next_sibling().text)
          df_source['Terms Of Service'][i] =   lab.find_next_sibling().text


    #print(df_source)

  return df_source


def download_meta_url(df_sourceCode, num_Splits):
  # Split dataframe
  dtframe_splited  = np.array_split(df_sourceCode, num_Splits) # max workers
  tasks = []

  for split in range(len(dtframe_splited)):
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(dtframe_splited)) as executor:
      # Download dataframes splited
      tasks.append(executor.submit(_download_meta_url, dtframe_splited[split]))

  df_temp = pd.DataFrame()
  # Union
  for result in tasks:
    df_temp = df_temp.append(result.result())

  return df_temp

df_FRAME_metaData = pd.DataFrame()
df_FRAME_metaData = download_meta_url(df_FRAME, 5)
df_FRAME_metaData

# Meta_Url could be used to check for updates on the source website. That uses only +600 web requests instead of +15k
# save a copy of the original dataframe to check for updates based on the meta url or other fields
df_FRAME_metaData.reset_index(inplace=True)
df_FRAME_metaData

from datetime import datetime
datetime = datetime.now()

## Export the original + Meta_Url
# To CSV (index True 0,1,2...)
df_FRAME_metaData.to_csv(r'/content/FRAME_' + datetime.now().strftime('%d_%m_%Y') + '.csv', index = True, header = True)

# To JSON (columns format index True 0,1,2...)
df_FRAME_metaData.to_json(r'/content/FRAME_' + datetime.now().strftime('%d_%m_%Y') + '.json')