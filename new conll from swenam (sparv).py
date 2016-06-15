# -*- coding: utf-8 -*-

# Shellscript for using the tokenization provided by Språkbankens tool Sparv. Make sure the files to be uploaded are in utf-8 (use iconv for quickly encoding multiple files).
# for f in ../text_files/utf8/*; do curl -X POST -F files[]=@"/Volumes/320/tjarles/Google Drive/729A97/Projekt/SweNam-100-test-files+answer_file/text_files/utf8/${f##*/}" https://ws.spraakbanken.gu.se/ws/sparv/v1/upload? > data.tmp;  grep -E "link" data.tmp | sed -E "s/.*link='(.*)'.*/\1/g" | xargs curl > tmp.zip; unzip tmp.zip; done

import os, sys
import fileinput
import codecs
from bs4 import BeautifulSoup
import nltk
import re
from re import split as resplit



# Informaton about all the textfiles
all_files = {}
# Current entities are changed in functions and made global
global current_NEs

gold_file = codecs.open("SweNam-goldstandard-answer-utf-8.txt", "r", encoding='utf-8')
for line in gold_file:
    if line[:6] == "<file>":
        file_name = line[6:].strip()
        # The different named entities related to each file
        names = []
        places = []
        companies = []
        times = []
    elif line[:6] == "<name>":
        NEs = re.split(", |,", line[6:].strip())
        #Some lists contained empty string (when gold ends with comma without new NE). This removes them.
        names = [x for x in NEs if x]
    elif line[:7] == "<place>":
        NEs = re.split(", |,", re.sub(' +',' ', line[7:].strip()))
        places = [x for x in NEs if x]
    elif line[:9] == "<company>":
        NEs = re.split(", |,", line[9:].strip())
        companies = [x for x in NEs if x]
    elif line[:6] == "<time>":
        NEs = re.split(", |,", line[6:].strip())
        times = [x for x in NEs if x]
    elif line[:7] == "</file>":
        all_files[file_name] = {"names":names, "places":places, "companies":companies, "times":times}


gold_file.close()

def firstFill(file_name):
    # print(file)
    # print(all_files[file_name]["names"])
    global current_NEs
    print("\n" + file)
    # current_NEs = {"name":all_files[file_name]["names"].pop(0), "place":all_files[file_name]["places"].pop(0), "company":all_files[file_name]["companies"].pop(0), "time":all_files[file_name]["times"].pop(0)}
    try:
        current_NEs["name"] = all_files[file_name]["names"].pop(0)
    except:
        current_NEs["name"] = None
    try:
        current_NEs["place"] = all_files[file_name]["places"].pop(0)
    except:
        current_NEs["place"] = None
    try:
        current_NEs["company"] = all_files[file_name]["companies"].pop(0)
    except:
        current_NEs["company"] = None
    try:
        current_NEs["time"] = all_files[file_name]["times"].pop(0)
    except:
        current_NEs["time"] = None

#Returns a set of the different word lenghts of the NEs in the file.
def getNELengths():
    NELengths = set()
    for NE in list(current_NEs.values()):
        if NE is None:
            continue
        else:
            NELengths.add(len(NE.split()))
    return NELengths

def refill(file_name, NE):
    if NE == "name":
        try:
            current_NEs["name"] = all_files[file_name]["names"].pop(0)
        except:
            print("Out of names to pop. Setting None.")
            current_NEs["name"] = None
    elif NE == "place":
        try:
            current_NEs["place"] = all_files[file_name]["places"].pop(0)
        except:
            print("Out of places to pop. Setting None.")
            current_NEs["place"] = None
    elif NE == "company":
        try:
            current_NEs["company"] = all_files[file_name]["companies"].pop(0)
        except:
            print("Out of names names. Setting None.")
            current_NEs["company"] = None
    elif NE == "time":
        try:
            current_NEs["time"] = all_files[file_name]["times"].pop(0)
        except:
            print("Out of times to pop. Setting None.")
            current_NEs["time"] = None

def isNotOnlyDot(text):
    if len(text) > 1:
        return True
    else:
        return False

def splitNEWithDot(words, NEs_in_file):
    word_count=0
    for word in words:
        if "." in word and isNotOnlyDot(word) and word not in ne_with_dot and word.split(".") is not None:
            NEs_for_file = NEs_in_file + list(current_NEs.values())
            for NE in NEs_for_file:
                if NE is None:
                    continue
                splitted_NE = NE.split()

                for NE_part in splitted_NE:
                    if NE_part in word and len(word.strip().split(".")) > 1:
                        split_words = word.split(".")
                        split_words.insert(1, ".")
                        # print("split words: "+split_words)
                        # print("split word: " + word + " to: " + str(split_words))
                        # print("split_words: " + str(split_words))
                        words[word_count:word_count+1] = split_words
                        # print("words after: " + str(words))
        # else:
        #     words.append(word)
        word_count+=1
    return words

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

def checkIfNE(words, word_count):
    ordered_NE_sizes=sorted(getNELengths(), reverse=True)
    # Loop over all sizes of the NEs.
    for NE_size in ordered_NE_sizes:
        # print("Checks for NE of size " + str(NE_size))
        combined_str=""
        for size_c in range(NE_size):
            try:
                combined_str += " " + words[word_count+size_c]
            except:
                #print("Last word in sentence.")
                break
        ##################################
        #DECOMENT BELOW TO DEBUG MATCHING#
        ##################################
        # print("Currently checks for: " + str(current_NEs))
        # print("Text: " + combined_str)

        if combined_str.strip() in list(current_NEs.values()):
            # Probably current NE, if unlucky gets wrong key/NE if two similar NEs in current_NE
            key = list(current_NEs.keys())[list(current_NEs.values()).index(combined_str.strip())]
            # print("Matched '" + combined_str.strip() + "' as '" + key + "'.")
            refill(file, key)
            return (combined_str.strip(), key, NE_size)
    return None




# Luckily the only two (added only nr) NE with ".".
ne_with_dot = ["aftonbladet.se", "klockan 01.52", "01.52"]
files_with_NE_left = 0

for file in all_files:
    # file = "0108236748703_UTR__00.html.txt"
    out_file = open("swenam-gold-test.conll", "a")
    sparv_file_name = file[:-3] + "utf8.xml"
    path = "sparv/korpus/" + sparv_file_name
    xml_file = codecs.open(path, "r", encoding='utf8')
    soup = BeautifulSoup(xml_file, 'html.parser')
    current_NEs = {}
    firstFill(file)
    sentence_nr = 0
    NEs_in_file = [item for sublist in list(all_files[file].values()) for item in sublist]

    sentences = soup.find_all("sentence")
    for sentence in sentences:
        words=[]
        word_count=0
        words_with_tags=sentence.contents
        previous_NE = ""
        for word_with_tags in words_with_tags:
            if word_with_tags.string.strip() != "":
                words.append(word_with_tags.string.strip())

        words = splitNEWithDot(words, NEs_in_file)

        #Main loop over words in sentence (
        while word_count <= len(words):
            # Make new lines for each sentence
            if word_count == len(words):
                out_file.write("\n")
                word_count+=1
                continue

            NE_entity_and_size = checkIfNE(words, word_count)
            if NE_entity_and_size is not None:
                inside_counter = NE_entity_and_size[2]

                while inside_counter > 0:

                    if inside_counter == NE_entity_and_size[2]:
                        out_file.write(str(word_count+1) + "\t" +
                                        words[word_count] + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" +
                                        "B" + "\t" +
                                        NE_entity_and_size[1] + "\t" + "_" + "\n")
                        inside_counter -= 1
                    else:
                        out_file.write(str(word_count+1) + "\t" +
                                        NE_entity_and_size[0].split()[-inside_counter] + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" +
                                        "I" + "\t" +
                                        NE_entity_and_size[1] + "\t" + "_" + "\n")
                        inside_counter -= 1

                word_count += NE_entity_and_size[2]
                continue

            else:
                out_file.write(str(word_count+1) + "\t" +
                                words[word_count] + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" + "_" + "\t" +
                                "O" + "\t" +
                                "_" + "\t" + "_" + "\n")

            word_count+=1


    # After having gone through every sentence in the file all NEs should be placed
    print("\nAsserting that all NE in " + file + " was assigned.")
    print("Values left (if any): " + str(all_files[file]))
    for value in current_NEs.values():
        # print("Currently unassigned value: " + str(value))
        if value is not None:
            files_with_NE_left += 1
        assert value is None

NEs_left = 0
for x in all_files.values():
    for y in x.values():
        NEs_left += 1

if files_with_NE_left > 0:
    print("\n" + str(files_with_NE_left) + " NEs are clogging up the rest " + str(NEs_left) + ".")

out_file.close()
