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
host = "192.168.0.1"
port = 22
username = "robozinho"
password = "12345"

query = 'SELECT nuImsi FROM modem;'

#CRIANDO METODOS

engine = create_engine("mysql+pymysql://{user}:{pw}@192.168.0.1/{db}".format(user="USUARIO",pw="1234",db="operadora"))

def open_connection():
    conn = mysql.connector.connect(
    host="192.168.0.1",
    user="USUARIO",
    password="1234",
    database="operadora")
    return conn
def close_connection(x):
    x.close()

def convert(list):
    return str(tuple(list))

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def getPquota(imsiPquota):
    
    
    comInicial = '''comando ssh restrito'''
    comListPquota = '''comando ssh restrito'''

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

    channel.send(comListPquota)
    while not channel.recv_ready():
        time.sleep(3)
    out = channel.recv(9999)
    pquota = out.decode("ascii")

    keys = find_between(pquota, 'Quota Name','Create Time')
    keys = 'Quota Name' + keys
    keys = keys + 'Create Time'
    keys = keys.replace("  ", "|")
    keys = keys.replace("||", "|")
    keys = keys.replace('\r', '')
    keys = keys.replace('\n', '')
    keyList = keys.split("|")

    values = find_between(pquota, 'Create Time', 'Total')
    values = values.replace("  ", "|")
    values = values.replace("||", "|")
    values = values.replace('\n', '')
    values = values.replace('\r', '')
    valueList = values.split("|")

    while '' in keyList:
        keyList.remove('')

    while '' in valueList:
        valueList.remove('')

    keyFinal = []
    for k in keyList:
        key = k.lstrip()
        keyFinal.append(key)

    valueFinal = []
    for v in valueList:
        value = v.lstrip()
        valueFinal.append(value)

    dictionary = dict(zip(keyFinal, valueFinal))
    json_object = json.dumps(dictionary, indent = 4)
    dicFinal = {'nuImsi': imsiPquota,'initial_value':dictionary['Initial Value'], 'balance':dictionary['Balance'], 'consumption':dictionary['Consumption']}

    return dicFinal

#ABRINDO CONEXÃO E EXTRAINDO IMSIS PARA GET

conn = open_connection()

dfImsi = pd.read_sql(query, con = conn).astype(str)

imsiList = dfImsi['nuImsi'].to_list()


headers = ['nuImsi','initial_value','balance','consumption']
dfPquota = pd.DataFrame(columns=headers)

dfImsi = pd.DataFrame()
dfImsi[['nuImsi']] = imsiList

for i in dfImsi.itertuples():
    imsi = i.nuImsi
    dicImsiQuota = getPquota(imsi)
    df = pd.DataFrame(dicImsiQuota, index=[0])
    dfPquota = dfPquota.append(df)

dfPquota[['dtRegistro']] = dataBanco

dfPquota.to_sql('imsi_consumo',con = engine, if_exists='append', index=False)

