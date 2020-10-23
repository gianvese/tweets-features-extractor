# tweets-features-extractor

Progetto di tesi mirato all'estrazione di features da un set di tweet.

## Introduzione

All'interno di questa directory si trovano i tre file: **from_id_scraper.py, features_extractor.py** e **data_profiling.py** che, se eseguiti in successione, ci permettono di:

 * creare un dataset di tweet a partire da una lista di link a quest'ultimi
 * estrarre un insieme di features dai tweet e ottenere una matrice che li rappresenti
 * eseguire il data profiling a partire dalla matrice calcolata al passo precedente

In questo README mostrerò come eseguire passo passo queste operazioni ma, in caso si volesse testare solamente l'estrattore di features, mostrerò anche come eseguire il solo file *features_extractor.py*.

Infine, nel caso in cui si vogliano consultare dei file d'esempio, ho lasciato nelle rispettive cartelle dei file che fanno riferimento ai vari anni presi in esame per l'analisi.

# Prerequisiti
**Attenzione**: si richiede Python3.6 e pip3 per l'esecuzione del codice perché sono stati sperimentati problemi d'installazione delle librerie aggiuntive con altre versioni.

Come prima cosa creare un ambiente virtuale dove andare ad installare le librerie aggiuntive richieste per il funzionamento e assicurarsi di installare **venv** per raggiungere lo scopo:
```bash
> pip3 install venv
```
e successivamente digitare:
```bash
> python3.6 -m venv ./virtual_env
```
per rendere attivo l'ambiente virtuale digitare:
```bash
> source virtual_env/bin/activate
```
Una volta attivato l'ambiente sarà possibile installare le librerie necessarie contenute in *requirementes.txt* mediante il comando:
```bash
> pip install -r requirements.txt
```
**NOTA**: nel momento in cui viene reso attivo l'ambiente virtuale i comandi **pip** e **python** utilizzeranno automaticamente la versione 3.6.

Per installare *wordnet* è necessario digitare:
```bash
> python 
>>> import nltk
>>> nltk.download('wordnet')
```

## Utilizzo

Una volta installati i requisti possiamo eseguire il codice.

In questa sezione vengono mostrate due casistiche di utilizzo con i comandi che possono essere copiati così come appaiono per ottenere i risultati desiderati.

**NOTA**: in caso si voglia ricavare i link di tweet differenti è necessario installare una libreria aggiuntiva, **snscrape** non presente in *requirements.txt* con il comando:
```bash
> pip install snscrape
```
e una volta installato, eseguire come nel seguente esempio:
```bash
> snscrape twitter-search "#marmomac since:2014-12-31 until:2020-09-29" > ./ids/some_file.txt
```
per ottenere i tweet contenenti l'hashtag "#marmomac" pubblicati nelle date indicate e che salverà i link trovati nel file da noi indicato.


### Esecuzione completa

Per l'esecuzione completa prenderemo come anno di riferimento i tweet del 2019.
Cominciamo dalla creazione del dataset con *from_id_scraper.py*, script che, preso un file di testo in input contenente i link ai tweet, recupera tramite le API di Twitter le informazioni necessarie per ogni tweet e le salva in un file CSV, situato in  *./datasets/*, utilizzabile per l'estrazione delle features:
```bash
> python from_id_scraper.py ./ids/marmomac_2019_tweets.txt ./datasets/marmomac_2019_tweets.csv
```
Il dataset creato verrà utilizzato come input per l'estrattore di features il quale richiede in input il path a quest'ultimo e il path del file dove verrà salvata la matrice di output:
```bash
> python features_extractor.py ./datasets/marmomac_2019_tweets.csv ./matrices/marmomac_2019_matrix.csv
```
Infine, per creare un report sulla matrice appena calcolata, utilizzando il data profiling di pandas con:
```bash
> python data_profiling.py ./matrices/marmomac_2019_matrix.csv ./data_profiling/marmomac_2019_matrix_profiling.html
```
### Esecuzione del solo estrattore

Nel caso si voglia testare il solo estrattore è possibile eseguire il seguente comando che prende un dataset precedentemente creato (in questo caso con i tweet del 2020) e il cui data profiling è presente nella directory *./data_profiling/*:
```bash
> python features_extractor ./datasets/marmomac_2020_tweets.csv ./matrices/marmomac_2020_matrix.csv
```
