#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import paramiko, time, re, json, pandas as pd, mysql.connector
from datetime import datetime, timedelta
from sqlalchemy import create_engine

#SETANDO VARIAVEIS DE DATA
tempo = datetime.now() - timedelta()
today = tempo.strftime('%Y-%m-%d')
dataBanco = tempo.strftime('%Y-%m-%d %H:%M:%S')

#SETANDO VARIAVEIS
imsiPquota = '000000000000000'
host = "192.168.0.1"
port = 22
username = "robozinho"
password = "teste"

query = 'SELECT nuImsi FROM modem;'

#CRIANDO METODOS

engine = create_engine("mysql+pymysql://{user}:{pw}@192.168.0.1/{db}".format(user="USER",pw="1234",db="operadora"))

def open_connection():
    conn = mysql.connector.connect(
    host="192.168.0.1",
    user="USER",
    password="1234",
    database="operadora")
    return conn
def close_connection(x):
    x.close()

def convert(list):
    return str(tuple(list))


def resetPquota(imsiPquota):
    
    
    comInicial = '''comando ssh restrito da empresa'''
    comReset = '''comando ssh restrito da empresa'''

    #CRIANDO SHELL EMULATOR

    client=paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host,port, username=username, password=password)
    channel = client.invoke_shell()
    out = channel.recv(9999)

    #CONECTANDO AO WEB SERVER

    channel.send(comInicial)
    while not channel.recv_ready():
        time.sleep(3)
    out = channel.recv(9999)
    saidaComandoInicial = out.decode("ascii")

    #COMANDO GET

    channel.send(comReset)
    while not channel.recv_ready():
        time.sleep(3)
    out = channel.recv(9999)
    pquota = out.decode("ascii")

    #CRIANDO SHELL EMULATOR

    client=paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host,port, username=username, password=password)
    channel = client.invoke_shell()
    out = channel.recv(9999)

    #CONECTANDO AO WEB SERVER

    channel.send(comInicial)
    while not channel.recv_ready():
        time.sleep(3)
    out = channel.recv(9999)
    saidaComandoInicial = out.decode("ascii")

    #COMANDO GET

    channel.send(comReset)
    while not channel.recv_ready():
        time.sleep(3)
    out = channel.recv(9999)
    pquota = out.decode("ascii")

    return pquota


# In[ ]:


#ABRINDO CONEXÃO E EXTRAINDO IMSIS PARA GET

conn = open_connection()

dfImsi = pd.read_sql(query, con = conn).astype(str)

imsiList = dfImsi['nuImsi'].to_list()

dfImsi = pd.DataFrame()
dfImsi[['nuImsi']] = imsiList

for i in dfImsi.itertuples():
    imsi = str(i.nuImsi)
    print('RESETANDO O IMSI: ' + imsi)
    resetLog = resetPquota(imsi)

