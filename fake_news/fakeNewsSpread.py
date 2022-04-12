#get tweets related to fake news hashtag

#HYPOTHESIS: People's sentiment in tweets has become increasingly mild as a reaction to rises/falls in cases/deaths over the past two years
#Country Basis plot the days case level alongside average sentiment per day/week/month

import pandas as pd
import json

#TWEET DATA FROM PREPROCESSED DF
with open("./processed_data/final_df.json", "r") as file:
    COVIDdf = pd.read_json(json.load(file))

topics = {'hypercapnia':0,
'George Soros':0,
'French Pasteur Institute':0,
'authorized euthanasia':0,
'Dr. Anthony Fauci':0,
'fauci':0,
'alter human DNA':0,
'microchip surveillance technology':0,
'microchip':0,
'infertility':0,
'infertile':0,
'sterile':0,
'aborted human fetal tissue':0,
'disappearing needles':0,
'miscarriage':0,
'prion diseases':0,
"Canadian lab":0,
"HIV":0,
"Bill Gates":0,
"manmade bioweapon":0,
"5G ":0,
"Colloidal silver":0,
"Miracle Mineral Solution":0,
"Garlic":0,
"vitamin C":0,
"Lemon and hot water":0
}

for tweet in COVIDdf['text']:
    for topic in topics:
        if topic.lower() in tweet.lower():
            count = topics[topic]+1
            topics.update({topic: count})


print({topic: value for topic, value in sorted(topics.items(), key=lambda item: item[1], reverse=True)})