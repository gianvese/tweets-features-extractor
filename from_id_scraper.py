import tweepy
import re
import csv
import sys
from tqdm import tqdm

# Check dei parametri
if len(sys.argv) != 3:
    print('USAGE: from_id_scraper.py input.txt output_file.csv')
    sys.exit(2)

# file di testo contenente i link 
input_file = sys.argv[1]
# file csv di output dove verrà creato il dataset
output_file = sys.argv[2]

# set utlizzato per immagazzinare gli id ricavati dal file di testo contenente i link dei tweet da analizzare
# questi verrano successivamente utilizzati per formulare l'interrogazione tramite API
ids = set()
tweets_list = [] #questa sara' una lista di liste dove indici i = tweet e indice j = attributo del tweet i-esimo

# questa funzione permette di recuperare le info necessarie utilizzando le API ufficiali
# a partire dall'ID di un tweet
def extract_tweepy_tweet_info(tweet_id):
	tweet = api.get_status(tweet_id, tweet_mode='extended')
	return tweet #info da ritornare

# questa funzione permette di ricavare gli id dei tweet partendo dai loro link
def get_ids(text_file, ids):
	file_to_read = open(text_file, 'r')
	lines = file_to_read.readlines()

	for line in lines:
		#cercare status/id
		id_string = re.search(r'(status/)(0-9)*', line)
		if id_string:
			ids.add(line[id_string.span()[1]:-1])	

############################## AUTENTICAZIONE ##############################
#chiavi generate da Twitter dopo richiesta per account developer

consumer_key = # *** insert your key here ***
consumer_secret = # *** insert your key here ***
access_token = # *** insert your key here ***
acess_token_secret = # *** insert your key here ***

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, acess_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)
############################################################################

# PATH dei file che contengono i link ai tweet da recuperare
get_ids(input_file, ids)

# ciclo per ricavare le info che cerchiamo, necessarie a formare il dataset
# viene fatta un0interrogazione ad ogni iterazione con i vari id trovati precedentemente
for tweet_id in tqdm(ids):
	tweet = extract_tweepy_tweet_info(tweet_id)

	#hashtags
	hashtags = ''
	for hashtag in tweet.entities['hashtags']:
		hashtags += ' ' + hashtag['text']

	#urls
	urls = ''
	for url in tweet.entities['urls']:
		urls += ' ' + url['expanded_url']

	mentions = ''
	for mention in tweet.entities['user_mentions']:
		mentions += ' ' + mention['screen_name']

	#lista degli attrbuti che andremo a salvare nel dataset
	attributes_list = [tweet.full_text, tweet.created_at, tweet.geo, tweet.lang, tweet.place, tweet.coordinates, tweet.user.favourites_count, tweet.user.statuses_count, tweet.user.description, tweet.user.location, tweet.user.id, tweet.user.created_at, tweet.user.verified, tweet.user.following, tweet.user.url, tweet.user.listed_count, tweet.user.followers_count, tweet.user.default_profile_image, tweet.user.utc_offset, tweet.user.friends_count, tweet.user.default_profile, tweet.user.name, tweet.user.lang, tweet.user.screen_name, tweet.user.geo_enabled, tweet.user.profile_background_color, tweet.user.profile_image_url_https, tweet.user.time_zone, tweet.id, tweet.favorite_count, tweet.retweeted, tweet.source, tweet.favorited, tweet.retweet_count, hashtags, urls, tweet.in_reply_to_status_id_str, mentions]
	tweets_list.append(attributes_list)

#38 colonne 
columns_names = ['text', 'created_at', 'geo', 'lang', 'place', 'coordinates', 'user.favourites_count', 'user.statuses_count', 'user.description', 'user.location', 'user.id', 'user.created_at', 'user.verified', 'user.following', 'user.url', 'user.listed_count', 'user.followers_count', 'user.default_profile_image', 'user.utc_offset', 'user.friends_count', 'user.default_profile', 'user.name', 'user.lang', 'user.screen_name', 'user.geo_enabled', 'user.profile_background', 'user.profile_image_url_https', 'user.time_zone', 'id', 'favorite_count', 'retweeted', 'source', 'favorited', 'retweet_count', 'hashtags', 'urls', 'reply', 'mentions']
with open(output_file, 'a', newline= '') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quoting = csv.QUOTE_NONNUMERIC)
    #scrittura della riga d'intestazione con i nomi delle colonne
    csv_writer.writerow(columns_names)
    #scrittura degli attributi recuperati su file
    for tweet in tweets_list:
        csv_writer.writerow(tweet)

print('Dataset creato in', sys.argv[2], '!')
