import string
from twitter_specials import *
import math
import csv
import json
labels = {"positive":0,"negative":1,"neutral":2,"irrelevant":3}
reversed_labels = {0:"positive",1:"negative",2:"neutral",3:"irrelevant"}
WCOUNT = 4
total = [0,0,0,0,0]
word_counts_dict={}
word_prob_dict = {}
def parsing():
    with open("data/labeled_corpus.tsv",encoding="utf-8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter='\t')
        for row in readCSV:
            line_arr = list(row)
            tweet = line_arr[0]
            tweet = clean_tweet(tweet, emo_repl_order, emo_repl, re_repl)
            words = tweet.split()
            word_set = set()
            punc = set(string.punctuation)
            label = str(line_arr[1])
            if label not in labels:
                continue
            for w in words:
                if '#' not in w and '@' not in w:
                    s = ""
                    for ch in w:
                        if (ch not in punc):
                            s += ch
                    w = s
                    word_set.add(w)

            for w in word_set:
                if w not in word_counts_dict:
                    word_counts_dict[w] = [0,0,0,0,0]
                word_counts_dict[w][WCOUNT]+= 1
                word_counts_dict[w][labels[label]]+=1
            total[WCOUNT]+=1
            total[labels[label]] += 1
        for w,counts in word_counts_dict.items():
            for i in range(4):
                if w not in word_prob_dict:
                    word_prob_dict[w] = [0,0,0,0]
                word_prob_dict[w][i]=word_counts_dict[w][i]/total[i]
    csvfile.close()

def classifier():
    with open("data/geo_twits_squares.tsv", encoding="utf-8") as csvfile:
        readCSV = csv.reader((line.replace('\0', '') for line in csvfile), delimiter='\t')
        output = []
        for row in readCSV:
            line_arr = list(row)
            latitude = line_arr[0]
            longitude = line_arr[1]
            prob = [0,0,0,0]
            tweet = clean_tweet(line_arr[2], emo_repl_order, emo_repl, re_repl)
            words = tweet.split()
            punc = set(string.punctuation)
            tested = 0
            for w in words:
                if '#' not in w and '@' not in w:
                    s = ""
                    for ch in w:
                        if (ch not in punc):
                            s += ch
                    w = s
                    if w in word_prob_dict:
                        tested = 1
                        try:
                            for i in range(4):
                                prob[i] = math.log(word_prob_dict[w][i])+math.log(total[i]/total[WCOUNT])
                        except:pass
            if tested == 1:
                row_output = [latitude,longitude, reversed_labels[prob.index(max(prob))]]
            else : row_output = [latitude,longitude, "irrelevant"]
            output.append(row_output)
        with open("locations_classified.tsv","w") as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t')
            writer.writerows(output)
    tsvfile.close()
    csvfile.close()
pos_dict = {}
def pscore():
    pos_dict = {}
    locations = None
    with open("locations_classified.tsv", encoding="utf-8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter='\t')
        for row in readCSV:
            line_arr = list(row)
            label = line_arr[2]
            if (line_arr[0], line_arr[1]) not in pos_dict:
                if locations != None:
                    pos_dict[locations] = (count[0]/count[-1] - count[1]/count[-1] + 1)/2
                locations = (line_arr[0], line_arr[1])
                count = [0.0, 0.0, 0.0, 0.0, 1.0]
                pos_dict[locations] = 0
                count[labels[label]] += 1
            else:
                count[labels[label]] += 1
                count[-1] += 1
                print(count[0])
                print(count[1])
                print("hahah")
        pos_dict[locations] = (count[0]/count[-1] - count[1]/count[-1] + 1)/2
        #I will do the json file as well here
        input = []
        for loc,score in pos_dict.items():
            dict = {}
            dict["score"]=score
            dict["g"]=float(loc[1])+0.025
            dict["t"]=float(loc[0])+0.025
            input.append(dict)
        with open("data.js","w") as jsonfile:
            jsonfile.write("var data =")
            json.dump(input,jsonfile)
if __name__ == '__main__':
    parsing()
    classifier()
    pscore()









