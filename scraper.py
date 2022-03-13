import pandas as pd

#whole dataset -> pandas frame
#data = pd.read_csv('covidvaccine.csv')

#available columns in covidvaccine.csv are: user_name,user_location,user_description,
#                       user_created,user_followers,user_friends,
#                       user_favourites,user_verified,date,text,
#                       hashtags,source,is_retweet

#import with only certain columns
data = pd.read_csv('covidvaccine.csv', usecols= ['user_location','date', 'text'])
print(data.head())