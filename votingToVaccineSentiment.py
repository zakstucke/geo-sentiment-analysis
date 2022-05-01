import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import pearsonr
voting = pd.read_csv('voter.csv')

s = [['AK', 0.25050000000000006], ['AL', 0.08312340425531915], ['AR', 0.11865483870967743], ['AZ', -0.03223119266055046], ['CA', 0.09892184655396619], ['CO', 0.07752125000000001], ['CT', 0.15261000000000002], ['DE', 0.21075], ['FL', 0.018672368421052632], ['GA', 0.08095530973451327], ['HI', 0.07167083333333334], ['IA', 0.11816538461538463], ['ID', -0.038569999999999986], ['IL', 0.055306376811594206], ['IN', 0.09969268292682928], ['KS', 0.1875267605633803], ['KY', 0.10670895522388059], ['LA', 0.05632828282828283], ['MA', 0.10600813953488372], ['MD', 0.06968197674418605], ['ME', 0.274475], ['MI', 0.09145344827586208], ['MN', 0.13173152173913044], ['MO', 0.10230925925925927], ['MS', 0.17624375], ['MT', -0.11596], ['NC', 0.09814930555555555], ['ND', -0.09116190476190475], ['NE', -0.017783673469387758], ['NH', -0.3098666666666667], ['NJ', 0.10344337349397591], ['NM', 0.05547619047619048], ['NV', 0.0672343137254902], ['NY', 0.10576875000000001], ['OH', 0.11129722222222223], ['OK', 0.0847659090909091], ['OR', 0.03113975903614458], ['PA', 0.12489030837004406], ['RI', 0.06273636363636363], ['SC', 0.1297433962264151], ['SD', 0.3665333333333334], ['TN', 0.1237990990990991], ['TX', 0.09217521367521368], ['UT', 0.240848], ['VA', 0.1909], ['VT', 0.0], ['WA', 0.08013673469387755], ['WI', 0.0832220588235294], ['WY', -0.08434]]
sentDict = {}
for i in s:
    sentDict.update({i[0]:i[1]})

    
def hypothesisTest(x, y, alpha):
    likelyDependent = False
    x = x[~np.isnan(x)]
    if len(x)<len(y):
        y = y[-len(x):]
    corr, p = pearsonr(x, y)
    #print('Correlation=%.3f, p=%.3f' % (corr, p))
    if p < alpha:
        likelyDependent = True
    return p, corr, likelyDependent



vaxDF = pd.DataFrame.from_dict(sentDict, orient='index', columns=['sent'])
df = voting.join(vaxDF, on='usa_state_code')
df = df.dropna()
print(df)
#df.to_csv('stateSetniment.csv')
print(hypothesisTest(df['percent_republic'], df['sent'], 0.05))

plt.bar(df['usa_state_code'], df['sent'])
plt.xticks(rotation=-90)
plt.title('Vaccine Sentiment by State')
plt.xlabel("State")
plt.ylabel('Sentiment Score')
plt.show()