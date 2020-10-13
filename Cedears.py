import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests


#Get list from all cedears (an Argentinian option for buying stocks from the US market)
url_all_cedears = 'https://www.infobursatil.com/listado-cedears/'
r = requests.get(url_all_cedears)
soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find('table')
cedear_info_columns = ['COMPANY_CODE', 'DESCRIPTION', 'RATIO_CONVERTION', 'FREQUENCY_DISTRIBUTION_EARNINGS']
ceadears_info = pd.DataFrame(columns = cedear_info_columns)
id_counter = 0

for row in table.findAll('tr'):
    if id_counter != 0:
        td = row.findAll('td')
        code = td[0].text
        description = td[1].text
        ratio = td[2].text.split(':')[0]
        frequency = td[3].text
        cedear_data = pd.DataFrame([[code, description, ratio, frequency]])
        cedear_data.columns = cedear_info_columns
        ceadears_info = ceadears_info.append(cedear_data, ignore_index=True)
    id_counter += 1

ceadears_info.RATIO_CONVERTION = ceadears_info.RATIO_CONVERTION.astype(str).astype(int) 

#Download the evolution of stocks prices for all cedears
cedear_prices = pd.DataFrame(columns = ['DATE', 'OPENING_PRICE', 'MAXIMUM_PRICE', 'MINIMAL_PRICE', 'CLOSING_PRICE', 'VOLUME', 'COMPANY_CODE'])
for cod in list(ceadears_info['COMPANY_CODE']): 
    url = f'http://www.rava.com/empresas/precioshistoricos.php?e=CEDEAR{cod}&csv=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    html = [str(v.replace('"', '')).split(',') for v in str(soup).split('\r\n')]
    data = pd.DataFrame(html, columns = html[0])

    #Transformations
    data.drop(index = 0, inplace = True)
    data.reset_index(inplace = True)
    data.drop(columns = ['index', 'openint'], inplace = True)
    data.fecha = pd.to_datetime(data.fecha)
    data.apertura = data.apertura.astype(float)
    data.maximo = data.maximo.astype(float)
    data.minimo = data.minimo.astype(float)
    data.cierre = data.cierre.astype(float)
    data.rename(columns={'fecha': 'DATE', 'apertura': 'OPENING_PRICE', 'maximo': 'MAXIMUM_PRICE', 'minimo': 'MINIMAL_PRICE', 'cierre': 'CLOSING_PRICE', 'volumen': 'VOLUME'}, inplace = True)
    data['COMPANY_CODE'] = cod
    data.dropna(inplace = True)
    cedear_prices = cedear_prices.append(data)


#Saving the final data
    cedear_prices.to_csv('prices_evolution.csv', sep = ',', header = True, index = False)
    ceadears_info.to_csv('cedear_information.csv', sep = ',', header = True, index = False)
