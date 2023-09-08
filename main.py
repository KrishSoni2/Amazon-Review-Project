#Import all the neseccary files 
import json
import matplotlib.pyplot as plt
import gzip
import random
import array
from afinn import Afinn
import pandas as pd

#First unzip the file using this method so you can then run through it to find the asin's and product info
def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield eval(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

review = getDF('reviews_Office_Products.json.gz')

meta= getDF('meta_Office_Products.json.gz')
#-----------------------------------------------------

#Select a random reviewer from the file
review_length= len(review)
inx= random.randint(0,review_length)


#set the variables to the random number chosen
print('Reviewer Name: ',review.loc[inx]['reviewerName'])

#=====================================================
#Since the rest of the data is in the meta we have to go through the whole meta data and print out the product discription corresposnding to the asin from the randomly selected user in the review file
# Get the ASIN of the selected review
asin = review.loc[inx]['asin']

# Check if the ASIN is present in the 'meta' dataframe
if meta['asin'].isin([asin]).any():
  # Get the index of the corresponding row in the 'meta' dataframe
  meta_inx = meta[meta['asin'] == asin].index[0]
  
  # Get the product description and price
  if meta.loc[meta_inx]['price']:
    print()
    print('Price: $',meta.loc[meta_inx]['price'])
  else:
    pass

  print()
  description = meta.loc[meta_inx]['description']
  print('Product Description: ', description)

#------------------------------------------------------------
#Run a sentimental analysis on the product discription
afinn = Afinn()

# Get the product ASIN
asin = review.loc[inx]['asin']

# Find the product description in the meta data
product_meta = meta[meta['asin'] == asin]

# Get the product description
product_description = product_meta['description'].iloc[0]

if not isinstance(product_description, (str, bytes)):
    product_description = str(product_description)

# Use Afinn to classify the sentiment of the product description
sentiment = afinn.score(product_description)

# Print the sentiment
print()
print("Sentiment: ", sentiment)
print()
if sentiment > 0:
    print('Positive, The user liked this Product!!!')
elif sentiment < 0:
    print('Negative, The user didnt like this Product')
else:
    print('Neutral,The user was in the middle about this product')

#-------------------------------------------------------------------
print()
print('------------------------------------------------------')
print()
#Use Matplotlib to make a graph of all the also boughts and present it in a graph
#First make an empty list which will hold all the asin's of the also boughts 
also_bought_list = []
sentimental_analysis= []
if isinstance(meta.loc[meta_inx]['related'], dict) and 'also_bought' in meta.loc[meta_inx]['related'] and isinstance(meta.loc[meta_inx]['related']['also_bought'], list):
    for item in meta.loc[meta_inx]['related']['also_bought']:
        also_bought_list.append(item)
else:
    print()
    print("No 'also_bought' items found")

for asin in also_bought_list:
    # Check if the ASIN is present in the 'meta' dataframe
    if meta['asin'].isin([asin]).any():
        # Find the product description in the meta data
        product_meta = meta[meta['asin'] == asin]
        # Get the product description
        product_description = product_meta['description'].iloc[0]
        # Use Afinn to classify the sentiment of the product description
        sentiment = afinn.score(str(product_description))
        # Append the sentiment score to the sentimental_analysis list
        sentimental_analysis.append(sentiment)
    else:
        continue


# Create a dictionary to store the ASINs and their corresponding sentimental analysis
sentiment_dict = {}
for asin, sentiment in zip(also_bought_list, sentimental_analysis):
    sentiment_dict[asin] = sentiment

#---------------------------------------------------------------------------------
if len(also_bought_list)>0:
  also= also_bought_list.copy()
  sentimentaal=sentimental_analysis.copy()

  inx= sentimentaal.index(max(sentimentaal))

  highest= also[inx]
  print()
  print('The User would also like this product:')
  print('ASIN: '+highest)
  print()
  # Check if the ASIN is present in the 'meta' dataframe
  if meta['asin'].isin([highest]).any():
    # Get the index of the corresponding row in the 'meta' dataframe
    meta_inx = meta[meta['asin'] == highest].index[0]
    
    # Get the product description and price
    if meta.loc[meta_inx]['price']:
      print()
      print('price: $',meta.loc[meta_inx]['price'])
    else:
      pass

    print()
    description = meta.loc[meta_inx]['description']
    print('Product Description: ', description)

else:
  pass

#----------------------------------------------------------------------------------
# Create a horizontal bar chart
plt.barh(range(len(sentiment_dict)), list(sentiment_dict.values()), align='center')
plt.yticks(range(len(sentiment_dict)), list(sentiment_dict.keys()))
plt.xlabel('Sentiment Score')
plt.ylabel('ASIN')
plt.title('Sentiment Analysis of Also Bought Products')

# Show the bar chart
plt.show()