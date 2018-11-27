from konlpy.tag import Okt
from konlpy import utils
from collections import Counter, defaultdict
from math import log

okt = Okt()

def tagCheck(x):
	#tag = ['Josa', 'Suffix']
	tag = ['Noun', 'Verb', 'Adjective', 'Determiner', 'Adverb', 'Conjuction', 'Punctuation','Exclamation', 'Josa', 'Suffix', 'Foreign', 'Alpha', 'Number', 'Unknown', 'KoreanParticle', 'PreEomi', 'Eomi']
	return x[1] in tag

def countWord(document, label):
	worddic = defaultdict(int)
	worddic['docu_size'] = len(document)
	worddic.update(Counter(label))
	word_size_pos = 0
	word_size_neg = 0
	word_size = set()
	taglist = []
	"""
	#whitespace 이용
	for idx, query in enumerate(document):
		words = query.split()
		for word in words:
			worddic[(word, label[idx])] += 1
			word_size.add(word)
			if label[idx] == '1': word_size_pos += 1
			else: word_size_neg += 1"""

	#형태소분석기 이용
	for idx, query in enumerate(document):
		words = list(filter(tagCheck, okt.pos(query, stem=True)))
		for word in words:
			taglist.append(word[1])
			worddic[(word[0], label[idx])] += 1
			word_size.add(word[0])
			if label[idx] == '1': word_size_pos += 1
			else: word_size_neg += 1

	worddic['word_size_pos'] = word_size_pos
	worddic['word_size_neg'] = word_size_neg
	worddic['wordsize'] = len(word_size)
	return worddic

def calPredic(query, worddic):
	#whitespace 이용
	#queryWord = query.split()

	#형태소분석기 이용
	queryWord = [word[0] for word in list(filter(tagCheck, okt.pos(query, stem=True)))]

	predic_pos = log(worddic['1']) - log(worddic['docu_size'])
	predic_neg = log(worddic['0']) - log(worddic['docu_size'])
	for word in queryWord:
		predic_pos += log((worddic[(word, '1')] + 1) / (worddic['word_size_pos'] + worddic['word_size']))
		predic_neg += log((worddic[(word, '0')] + 1) / (worddic['word_size_neg'] + worddic['word_size']))
	
	return 1 if (predic_pos >= predic_neg) else 0

#from train data, making word count dictionary
with open("ratings_train.txt", 'r') as file:
	header = file.readline().split()

	body = file.read().splitlines()
	id = []
	document = []
	label = []
	for row in body:
		id.append(row.split('\t')[0])
		document.append(row.split('\t')[1])
		label.append(row.split('\t')[2])

worddic = countWord(document, label)

#new file input for labeling
with open("ratings_test.txt", 'r') as file:
	header = file.readline().split()

	body = file.read().splitlines()
	id = []
	document = []
	for row in body:
		id.append(row.split('\t')[0])
		document.append(row.split('\t')[1])

label = []
for query in document:
	label.append(calPredic(query, worddic))

#ouput file including label
with open("ratings_result.txt", 'w') as file:
	file.write(f"{header[0]}\t{header[1]}\t{header[2]}\n")
	for idx, id_num in enumerate(id):
		data = f"{id_num}\t{document[idx]}\t{label[idx]}\n"
		file.write(data)
