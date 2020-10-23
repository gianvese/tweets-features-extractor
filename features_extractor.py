import string
import re
from nltk.tokenize import TweetTokenizer
from emoji import UNICODE_EMOJI
import csv
import numpy as np
import sys
from collections import Counter
from string import punctuation
from nltk.corpus import wordnet as wn # per calcolo OOV ratio

# check dei parametri
if len(sys.argv) != 3:
    print('USAGE: features_extractor.py path_to_dataset.csv output_file.csv')
    sys.exit(2)

# percorso per il dataset dal quale verranno estratte le features
input_file = sys.argv[1]
# file csv dove verrà salvata la matrice di output
output_file = sys.argv[2]

# funzione che controlla la presenza di url nel tweet
# ritorna True in caso positivo, False altrimenti
def hasURL(row):
    result = False
    if row[35]:
        result = True
    return result

# funzione che controlla se il tweet è di risposta
# ritorna True in caso positivo, False altrimenti
def isReply(row):
    reply = row[36] # contiene stringa con ID del tweet a cui si risponde
                    # se non è di risposta contiene None
    result = False

    if reply:
        result = True
    
    return result

# funzione che consente di identificare un retweet e che ritorna lp screen_name dell'utente
# di cui è stato fatto retweet, altrimenti ritorna una stringa vuota 
def isRT(tweet):
    rt_user = ''        
    ed_tweet = ''   
    potential_rt = '' 
    # insime di punteggiatura che verrà poi tolta da dalle parole analizzate
    my_punctuation = (':', '“', '\"', '@', '.', ',')  
    # cerca la sigla 'rt' in tutte le sue possibili forme 
    rts = re.search(r'^(RT |rt |RT|rt| RT| rt| RT | rt )(@\w*| \w*)?[: ]', tweet)

    if rts:
        # uniforma la sigla 'rt' in 'RT'
        # in caso una delle forme non sia presente, replace() non fa nulla
        forma1 = tweet
        forma2 = forma1.replace('RT ', "RT", 1)
        forma3 = forma1.replace('rt ', "RT", 1)
        forma4 = forma1.replace(' RT ', "RT", 1)
        forma5 = forma1.replace(' rt ', "RT", 1)
        forma6 = forma1.replace('rt', "RT", 1)

        # cerchiamo quale dei replace ha avuto effetto e 
        if forma1 != forma2:
            ed_tweet = forma2  
        elif forma1 != forma3:
            ed_tweet = forma3  
        elif forma1 != forma4:
            ed_tweet = forma4  
        elif forma1 != forma5:
            ed_tweet = forma5  
        elif forma1 != forma6:
            ed_tweet = forma6  
        else:
            ed_tweet = tweet
            
    # cerchiamo le varie situazioni in cui potremmo trovare 'RT'
    rt = re.search(r'(RT\w+|RT@\w+|RT: \w+|RT.\w+|RT.\w+:|RT: @\w+:|RT: @\w+ |RT\( |RT\“@\w+:)', ed_tweet)      #così dovrebbe coprire tutti gli altri casi (però ne tira dentro altri che non sono veri RT)
    if rt:
        # esegue una prima pulizia della stringa
        ed_tweet = ed_tweet.replace('RT', '', 1)
        ed_tweet = ed_tweet.replace(':', ' :')
        ed_tweet = ed_tweet.replace('\"', ' \"')

        potential_rt = ed_tweet

    # va ad analizzare parola per parola 
    if potential_rt != '':
        tmp = potential_rt.split(' ')
        tmp_first_word = ' '
        
        for word in tmp:
            if len(word) > 1 and word.strip() != 'via' and word[0] != '#' and word != 'from':
                tmp_first_word = word.lower()

                for char in my_punctuation:
                    if char in tmp_first_word:
                        tmp_first_word = tmp_first_word.replace(char, '')

                if len(tmp_first_word) > 1:
                    break
            
        if tmp_first_word in users:
            rt_user = tmp_first_word
        else:
            # controlli necessari in caso il tweet in questione sia in inglese
            if 'via' in tmp:
                check = tmp[tmp.index('via') + 1].lower()
                check = ''.join(ch for ch in check if ch not in my_punctuation)
                
                if check in users:
                    rt_user = check       

            elif 'Via' in tmp:
                check = tmp[tmp.index('Via') + 1].lower()
                check = ''.join(ch for ch in check if ch not in my_punctuation)
                
                if check in users:
                    rt_user = check
    
    return rt_user      

# funzione che aggiorna le occorrenze degli url
def url_count(row):
    urls = row[35]
    # nel caso ci siano più url in un tweet
    urls = urls.split()
    for url in urls:
        if url in url_counter:
            # l'url è già comparso almeno una volta
            url_counter[url] += 1
        else:
            # prima apparizione per l'url
            url_counter[url] = 1

# funzione che ritorna la somma dei vari url_count presenti in un tweet
def get_sum_url_count(row):
    result = 0
    urls = row[35]
    urls = urls.split()
    for url in urls:
        result += url_counter[url]
    return result

# funzione che aggiorna il dizionario degli user.screeen_name appartenenti al dataset
def getUsers(row):
    # lower() utilizzata perché twitter non è case sensitive
    user = row[23].lower()
    users[user] = []
    return user

# funzione che cicla per prima nel dataset per raccogliere le info preliminari necessarie al calcolo delle varie features
def get_initial_info():
    counter = 0 # serve per contare n_righe
    with open(input_file, newline= '') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter = ',', quotechar = '"')
        header = next(csv_reader)   # serve per saltare la riga d'intestazione del dataset
        for row in csv_reader:
            tweet = row[0]
            user = getUsers(row)
            PScores[user] = round(1.0 - e, 4)       # tutti i punteggi 'popularity score' vengono inizializzati a 0.2
            mentionScores[user] = 0
            getOVVratio(tweet)
            getHashtags(row)
            url_count(row)      

            counter += 1

    return counter  # conterrà il numero di righe necessario per creare la matrice finale 

# funzione che aggiorna le occorrenze dei vari hashtag presenti in un tweet
def getHashtags(row):
    htgs = row[34]
    htgs = htgs.split()
    for htg in htgs:
        htg = htg.lower()       # lower() per non contare distintamente lo stesso hashtag scritto diversamente
        if htg in hashtags:
            # l'hashtag è già comparso almeno una volta
            hashtags[htg] += 1
        else:
            # prima apparizione per l'hashtag
            hashtags[htg] = 1

# funzione che calcola l'hashtagScore di un tweet
def getHashtagScore(row):
    result = 0.0
    htgs = row[34]
    htgs = htgs.split()
    for htg in htgs:
        htg = htg.lower()
        result += hashtags[htg]
    if result > 0:    
        result = result / len(htgs)  # divisione della somma delle istanze dei vari tweet per il numero di essi contenuto nel tweet
    return result

# ritorna il numero di volte in cui un autore di un tweet viene rtato da un utente
def getRN_ij(matrix, author, user):
    RN_ij = 0    #numero di volte in cui author è stato RTato da user
    RN_ij = matrix[row_per_user[user]][column_per_user[author]]

    return RN_ij


# funzione che prende in input l'autore di un tweet di cui è stato fatto retweet e 
# ne restituisce il Popularity Score
def PScoreCalculator(author):
    newScore = 0.0
    calculatedScores = 0.0
    changed = True
    initial_score = PScores[author]  # inizialmente sarà uguale a 0.2

    not_first_iteration = False
    # fino a quando il punteggio continuerà a cambiare, verrà eseguito il calcolo
    while changed:
        scores_to_sum = []      # per la sommatoria
        for RTuser in users_inverse_senzadoppioni[author]:      #RTuser sono gli utenti che hanno fatto RT di author
            RN_ij =  getRN_ij(rel_matrix, author, RTuser)       #numero d volte in cui author e' stato RTato da user 
            N_j = len(users_senzadoppioni[RTuser])              #numero di utenti di cui user ha fatto RT
            score = PScores[RTuser]
            newScore = (score * RN_ij) / N_j
            tmp_diff = abs(newScore - initial_score)

            rounded_tmp_diff = round(tmp_diff, 4)
            rounded_score = round(score, 4)
            rounded_newScore = round(newScore, 4)

            scores_to_sum.append(rounded_newScore)
 
        calculated_scores = sum(scores_to_sum)

        old_score = PScores[author]
        score_holder = round(1 - e + (e * calculated_scores), 4)
        PScores[author] = score_holder
        if not_first_iteration:             #se non è la prima iterazione procediamo col confronto
            difference = abs(score_holder - old_score)
            rounded_difference = round(difference, 4)
            if rounded_difference == 0.0:   # se il punteggio non è cambiato, possiamo uscire dal ciclo
                changed = False

        not_first_iteration = True        

# funzione che calcola le parole non appartenenti ad un dizionario delle seguenti lingue supportate
# {'en', 'fa', 'no', 'tr', 'pl', 'et', 'ht', 'nl', 'fr', 'pt', 'de', 'es', 'fi', 'ca', 'it', 'in'}
def getOVVratio(tweet):
    result = 0.0
    counterOOV = 0
    tweet_lenght = len(tweet)
    special_words = 0
    tokenizer = TweetTokenizer()        # separa in unità lessicali caratteristiche dei tweet (hashtag, ...)
    tt = tokenizer.tokenize(tweet)

    for token in tt:
        # se token non e' punteggiatura, se primo carattere non e' '#' o '@' e se token non e' una emoji
        token = token.lower()
        if token not in string.punctuation and token[0] != '#' and token[0] != '@' and token not in UNICODE_EMOJI:
            if not wn.synsets(token):
                counterOOV += 1
        else:
            special_words += 1 # i token non considerati per l'analisi verranno tolti dalla lunghezza della stringa
        
    result = counterOOV / (tweet_lenght - special_words)
    return result

# funzione che ritorna il numero di follower di un utente
def get_followerScores(followerScore, username):
    followerScores[username] = followerScore

# funzione che calcola il numero di volte che aggiorna il numero di volte in cui 
# un utente è stato menzionato in un tweet
def get_mentionScores(row):
    mentions = row[37]
    mentions = mentions.split()
    for user in mentions:
        user = user.lower()
        #ho tolto il controllo user in users perche' serve lo score anche di chi ha efffettuato un T che e' stato RT
        if user in mentionScores and mentionScores[user] > 0:
            mentionScores[user] = mentionScores[user] + 1
        else:
            mentionScores[user] = 1

# funzione che ritorna il numero di liste in cui un utente è stato inserito
def get_listScores(row):
    user = row[23].lower()
    listScore = int(row[15])
    listScores[user] = listScore

# funzione che permette di estrarre le features legate all'autorità di un utente e che completa
# il vettore rappresentate il tweet in esame
def authority_related_features_extractor():
    line_count = 0   

    with open(input_file, newline= '') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter = ',', quotechar = '"')
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                tweet = row[0]
                actual_user = row[23].lower()
                rt_user = isRT(tweet)
                followerScore = int(row[16])
                
                #nel caso in cui il tweet non abbia particolari relazioni con altri utenti (RT) allora non c'è bisogno di calcolare 
                #e i valori sono tutti e 3 uguali
                first_follower = followerScores[actual_user]      
                first_popularity = PScores[actual_user]
                first_mention = mentionScores[actual_user]
                first_list = listScores[actual_user]

                sum_follower = first_follower
                sum_popularity = first_popularity
                sum_mention = first_mention
                sum_list = first_list

                important_follower = first_follower
                important_popularity = first_popularity
                important_mention = first_mention
                important_list = first_list

                #se invece ci sono stati dei RT.....rt_user e' l'utente che ha postato in origini un Tweet mentre
                #user in user_inverse_senzadoppioni sono gli utenti che hanno RTato rt_user
                if rt_user != '':
                    sum_follower = followerScores[rt_user]
                    tmp_list = [followerScores[rt_user]]
                    for user in users_inverse_senzadoppioni[rt_user]:
                        sum_follower += followerScores[user]
                        tmp_list.append(followerScores[user])
                    
                    important_follower = max(tmp_list)

                    sum_popularity = PScores[rt_user]
                    tmp_list = [PScores[rt_user]]
                    for user in users_inverse_senzadoppioni[rt_user]:
                        sum_popularity += PScores[user]
                        tmp_list.append(PScores[user])
                    
                    important_popularity = max(tmp_list)

                    sum_mention = mentionScores[rt_user]
                    tmp_list = [mentionScores[rt_user]]
                    for user in users_inverse_senzadoppioni[rt_user]:
                        sum_mention += mentionScores[user]
                        tmp_list.append(mentionScores[rt_user])
                    
                    important_mention = max(tmp_list)

                    sum_list = listScores[rt_user]
                    tmp_list = [listScores[rt_user]]
                    for user in users_inverse_senzadoppioni[rt_user]:
                        sum_list += listScores[user]
                        tmp_list.append(listScores[user])

                    important_list = max(tmp_list)

                # completiamo il vettore che rappresenta il tweet in esame
                tweet_vectors[line_count].append(first_follower)
                tweet_vectors[line_count].append(first_popularity)
                tweet_vectors[line_count].append(first_mention)
                tweet_vectors[line_count].append(first_list)

                tweet_vectors[line_count].append(sum_follower)
                tweet_vectors[line_count].append(sum_popularity)
                tweet_vectors[line_count].append(sum_mention)
                tweet_vectors[line_count].append(sum_list)

                tweet_vectors[line_count].append(important_follower)
                tweet_vectors[line_count].append(important_popularity)
                tweet_vectors[line_count].append(important_mention)
                tweet_vectors[line_count].append(important_list)

                line_count += 1

# funzione che estrae le features legate al tweet in esame e prepara all'estrazione quelle 
# legate all'autorità cell'utente
def tweet_related_features_extractor():
    with open(input_file, newline= '') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter = ',', quotechar = '"')
        line_count = 0
        for row in csv_reader:
            # riga d'intestazione
            if line_count == 0:
                line_count += 1
            else:
                tweet_vectors[line_count] = []
                tweet = row[0]  
                
                rt_user = isRT(tweet)
                actual_user = row[23].lower()

                followerScore = int(row[16])

                if rt_user != '':
                    users[actual_user].append(rt_user)   #a fine ciclo avro' il dizionario "users" completo di liste con relazioni  
                containsURL = hasURL(row) 
                URLcount = get_sum_url_count(row)
                RTcount = row[33]  
                reply = isReply(row) 
                OOVratio = round(getOVVratio(tweet), 4)
                htgScore = round(getHashtagScore(row), 4)

                # al fine di poterle estarre dopo, vegnono chiamate le funzioni
                # per il calcolo delle features legate all'autorità
                get_followerScores(followerScore, actual_user)
                get_mentionScores(row)
                get_listScores(row)
                
                # iniziamo a costruire il vettore che rappresenterà il tweet in esame
                tweet_vectors[line_count].append(containsURL)
                tweet_vectors[line_count].append(URLcount)
                tweet_vectors[line_count].append(RTcount)
                tweet_vectors[line_count].append(htgScore)
                tweet_vectors[line_count].append(reply)
                tweet_vectors[line_count].append(OOVratio)
                line_count += 1

# manipola i vari dizionari che abbiamo popolato in modo da avere rappresentazioni
# diverse degli stessi dati che sono utili per il calcolo delle features
def data_manipolation():
    #popolo users_list, users_senzadoppioni, RTusers_list, users_inverse, users_inverse_senzadoppioni
    for user in users:
        if users[user]:
            users_list.append(user)
            
            if user not in users_senzadoppioni:
                    users_senzadoppioni[user] = []
            for u in users[user]:
                if u not in users_inverse:
                    users_inverse[u] = [user]
                else:
                    users_inverse[u].append(user)

                if u not in users_inverse_senzadoppioni:
                    users_inverse_senzadoppioni[u] = []
                    users_inverse_senzadoppioni[u].append(user)
                
                if u not in users_senzadoppioni[user]:
                    users_senzadoppioni[user].append(u)

# funzione che indicizza la matrice della relazioni tra autori e utenti che fanno RT
def matrix_maker():
    n_rows = 0
    n_columns = 0

    # le righe indicheranno un utente presente nel dataset
    for user in users:
        row_per_user[user] = n_rows
        n_rows += 1

    # le colonne saranno destinate ad autori i cui tweet sono stati RTati
    for user in users_inverse:
        column_per_user[user] = n_columns
        n_columns += 1    

    #inizializzo una matrice di zeri nella forma n_righe x n_colonne
    matrix = np.zeros((n_rows, n_columns)) 
    
    # indice i, j sarà diverso da zero solamente se utente i-esimo avrà
    # fatto RT dell'utente j-esimo
    for user in users:
        for rt_user, count in Counter(users[user]).items():
            matrix[row_per_user[user]][column_per_user[rt_user]] = count

    return matrix
    #potrebbe non servire, lo tengo solo in caso di necessità
    #for i in range(0, n_rows):
    #    for j in range(0, n_columns):

# CORRETTO
def get_final_matrix(d_list, n_righe):
    vector = np.array(d_list)
    final_matrix = np.reshape(vector, (n_righe, 18))
    return final_matrix

#************************************************************************************************************************************
#********************************************************* "MAIN" *******************************************************************
#************************************************************************************************************************************


#variabili globali
PScores = {}                        #associazione utente del dataset -> valore inizialmente posto a 0.2 e successivamente aggiornato
                                    #(PS: per maggior parte degli utenti restera' a 0.2)
e = 0.8                             #costante presente nella formula per calcolare PScore
#per features tabella 2
followerScores = {}                 #associazione utente del dataset -> punteggio 
mentionScores = {}                  #associazione utente del dataset -> punteggio 
listScores = {}                     #associazione utente del dataset -> punteggio 
                                    #(PS: gli utenti che sono stati RTati ma non sono presenti nel dataset hanno valore impostato a 0
                                    # ai fini di calcolare le features sum_* e important_*)

hashtags = {}                       #associazione hashtag -> numero di volte in cui questo compare in tutto il dataset
url_counter = {}                    #associazione url -> numero di volte in cui questo compare in tutto il dataset 

tweet_vectors = {}                  #associazione n.tweet (riga nel dataset) -> vettore di features ad esso associato
mega_list = []                      #conterra' il vettore contenente tutti i nostri vettori sul quale viene fatto numpy.reshape() per ottenere la matrice finale

users = {}                          #associazione user che ha fatto dei RT -> lista di user che l'utente chiave ha RTato  
users_senzadoppioni = {}            #associzione come sopra, eliminando i doppioni 
users_list = []                     #user che hanno fatto RT di quelli sopra
users_inverse = {}                  #associazione user che e' stato RTato -> lista con user che hanno fatto RT dell'utente chiave
users_inverse_senzadoppioni = {}    #associzione come sopra, eliminando i doppioni 


#per indicizzazione la matrice di relazioni retweet
row_per_user = {}
column_per_user = {}

n_righe = get_initial_info()        # otteniamo info iniziali e numero di righe che avrà la matrice
tweet_related_features_extractor()
data_manipolation()

rel_matrix = matrix_maker() 

# ora che abbiamo la matrice delle relazioni è possibile calcolare il Popularity Score
for author in users_inverse:
    PScoreCalculator(author)

authority_related_features_extractor()

# per ogni vettore calcolato, lo mette in un unico vettore che verrà poi rimodellato nella matrice finale
for l in tweet_vectors:
    mega_list.extend(tweet_vectors[l])       

# rimodellazione vettore unico
final_matrix = get_final_matrix(mega_list, n_righe)

# salvataggio della matrice calcolata
with open(output_file, 'w', newline= '') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quoting = csv.QUOTE_NONNUMERIC)
    csv_writer.writerow(('containsURL', 'URLcount', 'RTcount', 'htgScore', 'reply', 'OOVratio', 'first_follower', 'first_popularity', 'first_mention', 'first_list', 'sum_follower', 'sum_popularity', 'sum_mention', 'sum_list', 'important_follower', 'important_popularity', 'important_mention', 'important_list'))
    for row in final_matrix:
        csv_writer.writerow(row)

print('Matrice creata in', sys.argv[2], '!')
