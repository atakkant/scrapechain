# Sentiment analysis for tweets taken from http://help.sentiment140.com/for-students/
# These codes are populated with the help of the tutorials below:
# https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk#step-5-determining-word-density
# https://towardsdatascience.com/a-beginners-guide-to-sentiment-analysis-in-python-95e354ea84f6
# https://www.nltk.org/api/nltk.html

import pandas as pd
import nltk
from nltk.tag import pos_tag
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import twitter_samples
from nltk.stem.wordnet import WordNetLemmatizer
import re,string
from nltk import FreqDist
import random
from nltk import classify
from nltk import NaiveBayesClassifier
from nltk.tokenize import word_tokenize
import json
import csv


file = 'sample.csv'
columns = ["number","id","date","query","author","text"]
extracted_columns = ["text"]

def read_csv_file(file,columns):
    df = pd.read_csv(file,sep=',',encoding='latin-1',header=None)
    if columns:
        df.columns = columns
    return df

def create_csv_file(file,results,headers):
    with open(file,'w') as r:
        writer = csv.DictWriter(r,fieldnames=headers)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def open_json_file(file):
    f = open(file)
    data = json.load(f)
    return data.get('0')

def from_csv_to_json(file,new_file_name,columns):
    df = read_csv_file(file,columns)
    df.to_json(new_file_name)

def show_wordcloud(file,columns=None):
    df = read_csv_file(file,columns)

    stopwords = set(STOPWORDS)
    stopwords.update(["br","href"])
    if not columns:
        textt = " ".join(review for review in df[0])
    elif 'text' in columns:
        textt = " ".join(review for review in df.text)
    else:
        print('column not found in csv')
        return
    wordcloud = WordCloud(stopwords=stopwords).generate(textt)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('wordcloud11.png')
    plt.show()

print("loading tweet data for tokenization")
positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')


def lemmatize_sentence(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence

def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

stop_words = stopwords.words('english')
positive_cleaned_tokens_list = []
negative_cleaned_tokens_list = []

print("started removing noises")
for tokens in positive_tweet_tokens:
    positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

for tokens in negative_tweet_tokens:
    negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))


def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

print("preparing data to modeling")
all_pos_words = get_all_words(positive_cleaned_tokens_list)

freq_dist_pos = FreqDist(all_pos_words)

def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)

positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)


positive_dataset = [(tweet_dict, "Positive")
                     for tweet_dict in positive_tokens_for_model]

negative_dataset = [(tweet_dict, "Negative")
                     for tweet_dict in negative_tokens_for_model]

dataset = positive_dataset + negative_dataset

random.shuffle(dataset)

train_data = dataset[:7000]
test_data = dataset[7000:]

classifier = NaiveBayesClassifier.train(train_data)
print("Accuracy is:", classify.accuracy(classifier, test_data))

custom_tweets = []

sample = 'samp.csv'
json_file = 'samp.json'
from_csv_to_json(sample,json_file,columns=None)
tweet_dict = open_json_file(json_file)

for key,value in tweet_dict.items():
    custom_tweets.append(value)

custom_tokens = []
for tweet in custom_tweets:
    custom_tokens.append(remove_noise(word_tokenize(tweet)))

number_of_positives = 0
number_of_negatives = 0
for token in custom_tokens:
    status = classifier.classify(dict([tok,True] for tok in token))
    if status == 'Negative':
        number_of_negatives += 1
    elif status == 'Positive':
        number_of_positives += 1
positive_ratio = number_of_positives / (number_of_negatives+number_of_positives)
positive_float = "{:.2f}".format(positive_ratio)

print("result of analysis: ")
print("number of positive comments: %d"%number_of_positives)
print("number of negative comments: %d"%number_of_negatives)
print("positive comments percentage: ",end="")
print(positive_float)

results = [{'Status':'Number of Positives','Tweets':number_of_positives},{'Status':'Number of Negatives','Tweets':number_of_negatives}]
headers = ['Status','Tweets']
create_csv_file('results.csv',results,headers)
#link to report: https://datastudio.google.com/reporting/30e9fc6e-bf57-4f9c-96a1-83693a983a3f

print("preparing popular keywords image")
show_wordcloud(sample)
