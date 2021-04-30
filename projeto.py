# -*- coding: utf-8 -*-
"""projeto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PudnFMZgWbB-3Bvl_f896Snx-TmQlFpe
"""
import requests
import numpy as np
from flask import Flask, request, jsonify
import bs4 as bs
# pip install bs4
import urllib.request
#expressões regulares
import re
#natural lenguage toolkit
import nltk
import random
import string

nltk.download('punkt')

#outra biblio spacy para processamento de nlt(em pt/br)
#!pip uninstall spacy
#!pip install spacy==2.2.3


import spacy
spacy.__version__

nltk.__version__

"""Carregamento """

dados= urllib.request.urlopen('https://brasilescola.uol.com.br/biografia/alan-mathison.htm')
dados = dados.read()
dados

#Faz a reformatação
dados_html = bs.BeautifulSoup(dados, 'lxml')
dados_html

#agora remover as tags do html
paragrafos = dados_html.find_all('p')
len(paragrafos)

#primeiro paragrafo
paragrafos[0]

paragrafos[0].text

#vou remover todas as tags hmtl e deixar o texto todo puro
conteudo = ''
for p in paragrafos:
  conteudo += p.text

"""Pré-processamento"""

#Agora primeiramente vou deixar tudo minusculo
conteudo = conteudo.lower()
conteudo

#fazer a tokenização em sentenças
lista_sentencas = nltk.sent_tokenize(conteudo)
lista_sentencas

len(lista_sentencas)

type(lista_sentencas)

lista_sentencas[1]

spacy.cli.download("pt")

#usar o spacy para fazer alguns preprocessamentos
from spacy.lang.pt.examples import sentences
#portugues 
pln = spacy.load('pt_core_news_sm')
pln

stop_words = spacy.lang.pt.stop_words.STOP_WORDS

#remover palavras que não fazem sentido em frases
print(stop_words)

type(stop_words)

len(stop_words)

string.punctuation

def preprocessamento(texto):
  #primeiro remover urls
  texto = re.sub(r"https?://[A-Za-z0-9./]+", ' ', texto)

  #espaços em branco
  texto = re.sub(r" +",' ', texto)

  #lematização (extrair radical das palavras)
  documento = pln(texto)
  lista = []
  for token in documento:
    lista.append(token.lemma_)

  #pontuação
  lista = [palavra for palavra in lista if palavra not in stop_words and palavra not in string.punctuation]

  #percorre os elementos da lista e concatena as palavras da lista 
  lista = ' '.join([str(elemento) for elemento in lista if not elemento.isdigit()])

  return lista

#testar para ver se remove
texto_teste = 'https://www.google.com.br ' + lista_sentencas[0]
texto_teste

resultado = preprocessamento(texto_teste)
resultado

#aplicao preprocessamento para toda base de dados
lista_sentencas_preprocessadas = []
for i in range(len(lista_sentencas)):
  lista_sentencas_preprocessadas.append(preprocessamento(lista_sentencas[i]))

for _ in range(5):
  i = random.randint(0, len(lista_sentencas)-1)
  print(lista_sentencas[i])
  print(lista_sentencas_preprocessadas[i])
  print('----')

"""Frase de boas vindas"""

#pacote chat do NLTK
#chat e reflections(dicionarios com entradas e suas respectivas saidas)
import nltk
from nltk.chat.util import Chat, reflections

reflections

reflections_pt = {'eu': 'você',
                  'eu sou': 'você é',
                  'eu era': 'você era',
                  "eu iria": 'você iria',
                  "eu irei": 'você irá',
                  'meu': 'seu',
                  'você': 'eu',
                  'você é': 'eu sou',
                  'você era': 'eu era',
                  "você irá": 'eu irei',
                  'seu': 'meu'}

pares = [
    [
     r'oi|olá|opa|koe|tai?',
     ['olá', 'como vai?', 'tudo bem?','koe, tudo bem?','Oi']
    ],
    [
     r'qual é o seu nome?',
     ['Eu sou Optimus Prime. E mando esta mensagem para qualquer Autobot sobrevivente que esteja refugiando entre as estrelas. Nós estamos aqui. Nós estamos esperando.']
    ],  
    [
     r'(.*) idade?',
     ['Não tenho idade pois sou um chatbot :(']
    ], 
    [
     r'meu nome é (.*)',
     ['Olá %1, como você está hoje?']
    ],  
    [
     r'(.*) (cidade|país)',
     ['Sou de Cybertron']
    ], 
    [
     r'quit',
     ['Até breve', 'Foi bom falar com você. xauuu!']
    ]  
]



#Função para responder Chat
def responder_saudacao(texto):
  chat = Chat(pares, reflections_pt)
  oie = chat.respond(texto)
  return oie

#responder_saudacao('aeeddd')

"""TF IDF - TERM FREQUENCY - INVERSE DOCUMENT FREQUENCY"""

from sklearn.feature_extraction.text import TfidfVectorizer

frases_teste = lista_sentencas_preprocessadas[:3]
frases_teste

vetores_palavras = TfidfVectorizer()

palavras_vetorizadas = vetores_palavras.fit_transform(frases_teste)

type(palavras_vetorizadas)

palavras_vetorizadas

print(vetores_palavras.get_feature_names())

len(vetores_palavras.get_feature_names())

print(vetores_palavras.vocabulary_)

print(vetores_palavras.idf_)

palavras_vetorizadas.todense()

palavras_vetorizadas.todense().shape

#Similaridade cosseno
from sklearn.metrics.pairwise import cosine_similarity

palavras_vetorizadas[0].todense()

cosine_similarity(palavras_vetorizadas[0],palavras_vetorizadas[1])

cosine_similarity(palavras_vetorizadas[0],palavras_vetorizadas[2])

similaridade = cosine_similarity(palavras_vetorizadas[0],palavras_vetorizadas)
similaridade

similaridade.argsort()

i = similaridade.argsort()[0][-1]
i

i = i.flatten()
i

#funcaoresposta do chatbot
#Buscar na base da dados e mandar a resposta para o usuario
#
def responder(texto_usuario):
  resposta_chatbot = ''
  #adicionar dentro da lista a palavra adicionada pelo usuario 
  lista_sentencas_preprocessadas.append(texto_usuario)
  #calcular a similaridade a frase digitada pelo usuario com todas as frases que existem na base de dados
  #e retornar a mais parecida
  tfidf = TfidfVectorizer()
  #A base de dados inteira esta sendo convertida
  palavras_vetorizadas = tfidf.fit_transform(lista_sentencas_preprocessadas)
  #calcula a similaridade, retorna uma array com as similaridades
  similaridade = cosine_similarity(palavras_vetorizadas[-1],palavras_vetorizadas)
  
  indice_sentenca = similaridade.argsort()[0][-2]

  vetor_similar = similaridade.flatten()
  #ordenação
  vetor_similar.sort()
  #recebe o vetor que o chatbot encountrou
  vetor_encontrado = vetor_similar[-2]
  
  #se ele não retornou nada, retorna desculpe
  if (vetor_encontrado == 0):
    resposta_chatbot  = resposta_chatbot + 'Desculpa, não entendi :('
    return resposta_chatbot
  else:
    #caso ele tenha encontrado a resposta, eu retorno a reposta 
    resposta_chatbot = resposta_chatbot + lista_sentencas[indice_sentenca]
    return resposta_chatbot

continuar = True
print('Olá, sou o optimus prime e vou responder vc')
while (continuar == True):
  texto_usuario = input()
  texto_usuario = texto_usuario.lower()
  if (texto_usuario != 'quit'):
   if (responder_saudacao(texto_usuario)!= None):
      #se for saudacao ele sauda
      print('Chatbot:' + responder_saudacao(texto_usuario))
   else:
      #se não for saudaçao ele faz a bvusca
      print('Chatbot: ')
      print(responder(preprocessamento(texto_usuario)))
      lista_sentencas_preprocessadas.remove(preprocessamento(texto_usuario))
  else:
    continuar = False
    print('Chatbot: Autobots rodar!')

#-----------API FLASK--------------

app = Flask(__name__)

@app.route("/<string:txt>",methods=["POST"])
def conversar(txt):
    resposta = ''
    texto_usuario = txt
    #tratamentozinho
    texto_usuario = texto_usuario.lower()
    if (responder_saudacao(texto_usuario) != None):
        resposta = responder_saudacao(texto_usuario)
    else:
        resposta = responder(preprocessamento(texto_usuario))
        lista_sentencas_preprocessadas.remove(preprocessamento(texto_usuario))
    return jsonify({"Resposta:": resposta})

    
#Start application
app.run(port=8080,debug=False)

    
    
