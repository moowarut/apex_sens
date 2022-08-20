# import packages
import pandas as pd
import ast
import matplotlib.pyplot as plt
import seaborn as sns


#################
# Cleaning data #
#################

# Import xlsx file to pandas DataFrame
df_sens_clean = pd.read_excel('df_sens.xlsx')

# Copy those name which was romanized name in the first place to romanized name column
df_sens_clean.loc[df_sens_clean['Romanized Name'].isnull(), 'Romanized Name'] = df_sens_clean['Name']

# Fix birthdate to a proper date time format
df_sens_clean['Birth'] = pd.to_datetime(df_sens_clean['Birth'].str[2:12], errors='coerce')

# Create the age column based on difference between today and birthdate
now = pd.Timestamp('now')
df_sens_clean['Age'] = ((now - df_sens_clean['Birth'].dropna()) / pd.Timedelta('365.25 days')).round(0)

# Delete unwanted strings
df_sens_clean['Status'] = df_sens_clean['Status'].str.replace("\n", "")
df_sens_clean['Input'] = df_sens_clean['Input'].str.replace("\n", "")
df_sens_clean['Polling Rate'] = df_sens_clean['Polling Rate'].str.replace("Hz", "")
df_sens_clean['Approx. Total Earnings'] = df_sens_clean['Approx. Total Earnings'].str.replace("$", "")\
    .str.replace(",", "")
df_sens_clean['ALGS points (2020-21)'] = df_sens_clean['ALGS points (2020-21)'].str.replace(",", "")

# To get only the first option of sensitivity in case a player has multiple sensitivities
# This is done by delete everything after delimiters including " " and ","
df_sens_clean['Sensitivity'] = df_sens_clean['Sensitivity'].str.replace(" ", ",").str.split(",", 1).str[0]

# Assign a proper type for each column
df_sens_clean['Sensitivity'] = df_sens_clean['Sensitivity'].astype(float)
df_sens_clean['Polling Rate'] = df_sens_clean['Polling Rate'].astype(float)
df_sens_clean['Approx. Total Earnings'] = df_sens_clean['Approx. Total Earnings'].astype(float)
df_sens_clean['ALGS points (2020-21)'] = df_sens_clean['ALGS points (2020-21)'].fillna(0).astype(int)
df_sens_clean['Main Legends'] = df_sens_clean['Main Legends'].apply(ast.literal_eval)  # Revert to list type

# There were some errors of legend name which captured player's team by mistake
# Create a list of available legends and only get the result from intersections of two sets
available_legends = ['Ash', 'Bangalore', 'Bloodhound', 'Caustic', 'Crypto', 'Fuse', 'Gibraltar', 'Horizon', 'Lifeline',
                     'Loba', 'Mad Maggie', 'Mirage', 'Octane', 'Pathfinder', 'Rampart', 'Revenant', 'Seer', 'Valkyrie',
                     'Wattson', 'Wraith']
df_sens_clean['Main Legends'] = df_sens_clean['Main Legends'].apply(lambda x: list(set(x) & set(available_legends)))

# Manually calculated eDPI
df_sens_clean['eDPI_manual'] = df_sens_clean['DPI'] * df_sens_clean['Sensitivity']

# Check the DataFrame
print(df_sens_clean)

# Check the type of each column
print(df_sens_clean.dtypes)

# Export the cleaned table to the existing Excel file as a new sheet
with pd.ExcelWriter('df_sens.xlsx', engine='openpyxl', mode='a') as writer:
    df_sens_clean.to_excel(writer, sheet_name='table_cleaned')


##############################################
# General information about Apex pro players #
##############################################

# Get the basic information of dataframe
print(df_sens_clean.info())

# Get the summary statistics
print(df_sens_clean.describe())


#########################################
# Distribution of Apex pro players eDPI #
#########################################

# Print summary statistics
print(df_sens_clean['eDPI_manual'].describe().apply('{:,.1f}'.format))

# Use seaborn to create distribution plot of eDPI
sns.displot(data=df_sens_clean, x='eDPI_manual', kde=True, bins=30)
plt.title("Distribution of Apex pro players eDPI")
plt.show()
plt.clf()


# Distribution by status
# Print summary statistics
print(df_sens_clean.groupby('Status')['eDPI_manual'].describe().applymap('{:,.1f}'.format))

# Use seaborn to create distribution plot of eDPI for each status
sns.displot(data=df_sens_clean, x='eDPI_manual', kind='kde', hue='Status')
plt.title("Distribution of Apex pro players eDPI")
plt.show()
plt.clf()


# Regression plot of eDPI on Age
# Use seaborn to create regression plot of eDPI on age
sns.jointplot(data=df_sens_clean, x='Age', y='eDPI_manual', kind='reg')
plt.title("Regression plot of eDPI on Age", loc='left')
plt.show()
plt.clf()


# Main legends count
# Explode the Main Legends column (for those players who have more than one main legends)
df_sens_explode = df_sens_clean.explode('Main Legends')

# Use seaborn to create count plot of main legends used by players
ax = sns.countplot(data=df_sens_explode, y='Main Legends', order=df_sens_explode['Main Legends'].value_counts().index)
for p in ax.patches:
    ax.annotate('{}'.format(p.get_width()), (p.get_width(), p.get_y()+0.6))
plt.title("Main legends count")
plt.show()
plt.clf()


# Box plot of eDPI by legend
# Use seaborn to create box plot of eDPI by legend
sns.boxplot(data=df_sens_explode, x='eDPI_manual', y='Main Legends', order=df_sens_explode['Main Legends']
            .value_counts().index, fliersize=2)
plt.title("Box plot of eDPI by legend")
plt.show()
plt.clf()


# Box plot of eDPI by legend type (ignored outliers)
# Assign legend type as a new column of the dataframe
df_sens_explode['Legend Type'] = \
    ["Movement" if i in ['Wraith', 'Pathfinder', 'Octane', 'Valkyrie', 'Horizon']
     else "Non-movement" for i in df_sens_explode['Main Legends']]

# Print summary statistics
print(df_sens_explode.groupby('Legend Type')['eDPI_manual'].describe().applymap('{:,.1f}'.format))

# Use seaborn to create box plot of eDPI by legend type
ax = sns.boxplot(data=df_sens_explode, x='eDPI_manual', y='Legend Type', showfliers=False)
plt.title("Box plot of eDPI by legend type (ignored outliers)")
ax.set_yticklabels(('Movement \n (Wraith, Pathfinder, Octane, \n Valkyrie, Horizon)', 'Non-movement (Others)'))
plt.show()
plt.clf()


# eDPI mode
print(df_sens_clean['eDPI_manual'].mode())
