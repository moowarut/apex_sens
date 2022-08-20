# import packages
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


############################################
# Getting the main mouse sensitivity table #
############################################

# Specify url
url = 'https://liquipedia.net/apexlegends/List_of_player_mouse_settings/001-400'

# Package the request, send the request and catch the response: r
r = requests.get(url)

# Extracts the response as html: html_doc
html_doc = r.text

# Create a BeautifulSoup object from the HTML: soup
soup = BeautifulSoup(html_doc, features='lxml')

# Get the main table of the page
table = soup.find_all('table')

# Put in DataFrame having player alias as index
df_sens = pd.read_html(str(table), index_col='Player')[0]

# Only get the columns of interest
df_sens = df_sens[['eDPI', 'DPI', 'Sensitivity', 'Polling Rate', 'Mouse']]
# df_sens = df_sens[:5] # Experiment by selecting just some parts of the data

# Check the DataFrame
print(df_sens)


##############################################################################
# Iterating over Player column to get more information in each player's page #
##############################################################################

print('Player being processed:')

# Iterate over each player to get more information
for name in df_sens.index:
    print(name)  # Print alias of the player being processed

    # Create the url and do the same process as getting the main sensitivity table
    sub_url = 'https://liquipedia.net/apexlegends/' + name
    sub_r = requests.get(sub_url)
    sub_html_doc = sub_r.text
    sub_soup = BeautifulSoup(sub_html_doc, features='lxml')

    # Information of interest is tagged as div, class = infobox-cell-2
    result = sub_soup.find_all("div", {"class": "infobox-cell-2"})
    legend_result = sub_soup.find_all("img", {"height": "25"})

    # Create a list which more information will be added and later converted to dictionary
    base_list = ['Player', name]

    # Add more information to the previous list
    for res in result:
        base_list.append(res.text)

    # Convert to dictionary
    player_dict = {base_list[i].replace(":", ""): base_list[i + 1] for i in range(0, len(base_list), 2)}

    # Replace main legends' information from the correct source (<img alt="xxx">)
    legend_revised = str(
        [legend['alt'] for legend in legend_result if legend['alt'] != ""])  # Firstly convert to string to avoid error
    player_dict.update({'Main Legends': legend_revised})

    # Iterate over key and value pairs in dictionary and added them to the main sensitivity table
    for key, value in player_dict.items():
        df_sens.loc[name, key] = value

    # Pause for 20 seconds (2 seconds at least according to Liquipedia's rule) before performing next loop
    time.sleep(20)

# Only get the columns of interest
df_sens = df_sens[
    ['eDPI', 'DPI', 'Sensitivity', 'Polling Rate', 'Mouse', 'Name', 'Romanized Name', 'Birth', 'Country', 'Status',
     'Approx. Total Earnings', 'ALGS points (2020-21)', 'Input', 'Main Legends']]

# Check the DataFrame
print(df_sens)

# Export to .xlsx file
df_sens.to_excel('df_sens.xlsx', sheet_name='table_raw')
