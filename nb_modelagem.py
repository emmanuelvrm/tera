# -*- coding: utf-8 -*-
#Nb_modelagem.ipynb


# Grupo Games


##########################
# Importando bibliotecas #
##########################


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import random
import streamlit as st

##Puxando as bases de dados
st.write('Iniciando aplicação...')

df = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/igdb_games.csv')
df_igdb = df[['game_id','game_name','theme_name','genre_name','platforms_name']]
df_twitch_vods = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/df_twitch.csv')

df_twitch_vods['duration_minutes'] = pd.to_timedelta(df_twitch_vods['duration']).dt.total_seconds() / 60
df_igdb = df_igdb.drop('game_id',axis=1)
df_twitch_vods = df_twitch_vods .drop('game_id',axis=1)
df_twitch_vods.drop_duplicates(subset=['stream_id'],inplace=True)



##Juntando os DFs e iniciando tratativas

#Alguns nomes de jogos e usuários podem estar em cases diferentes mas serem repetidos
df_igdb['game_name'] = df_igdb['game_name'].str.lower()
df_twitch_vods['game_name'] = df_twitch_vods['game_name'].str.lower()
df_twitch_vods['user_name'] = df_twitch_vods['user_name'].str.lower()
df_geral = pd.merge(df_igdb, df_twitch_vods, on=["game_name"])
df_geral2 = df_geral[['game_name','theme_name','platforms_name','stream_id','user_name','published_at','duration','view_count','duration_minutes',]]
df_geral3 = df_geral[['game_name','genre_name','platforms_name','stream_id','user_name','published_at','duration','view_count','duration_minutes']]
df_geral2.rename(columns={'theme_name':'genre_name'},inplace=True)
df_geral = pd.concat([df_geral3, df_geral2])
df_geral.dropna(inplace=True)
#Dropando as entradas duplicadas
df_geral.drop_duplicates(subset=['stream_id'],inplace=True)
# Convertendo as unidades de tempo
df_geral['duration'] = pd.to_timedelta(df_geral['duration'])
df_geral['published_at'] = pd.to_datetime(df_geral['published_at'])
# Excluindo as transmições com menos de 30 minutos
df_geral = df_geral[df_geral['duration'] > '30m']
#Separando o mês
df_geral['month'] = pd.DatetimeIndex(df_geral['published_at']).month
df_geral = df_geral[df_geral['month'] > 7]

st.write('Carregando dados...')

##Df final

#############################
# DF de jogos para consulta #
#############################

df_games1 = df_igdb[['game_name','theme_name']]
df_games2 = df_igdb[['game_name','genre_name']]
df_games1.rename(columns={'theme_name':'genre_name'},inplace=True)
df_games = pd.concat([df_games1, df_games2])
df_games.dropna(inplace=True)
ajuste = df_games.groupby('genre_name')['game_name'].value_counts().to_frame()
ajuste.rename(columns={'game_name' : 'ajuste'}, inplace=True)
ajuste = ajuste['ajuste'].to_frame().reset_index()
ajuste.rename(columns={'ajuste' : 'descarte'}, inplace=True)
ajuste.drop(['descarte'],axis=1,inplace=True)
df_games = ajuste

# Cria Data Frame com jogos e quantidade de vezes que foi streamado
df_game_streams = df_geral.groupby('game_name')['stream_id'].count().to_frame()
df_game_streams.rename(columns={'stream_id' : 's'}, inplace=True)
df_game_streams = df_game_streams['s'].to_frame().reset_index()
df_game_streams.rename(columns={'s' : 'streams'}, inplace=True)
# Filtrando usuario por genero
user_by_gen = (df_geral.groupby(['user_name'])['genre_name'].value_counts()).to_frame()
user_by_gen.rename(columns={'genre_name' : 'genere'}, inplace=True)
user_by_gen = user_by_gen['genere'].to_frame().reset_index()
user_by_gen.rename(columns={'genre' : 'freq'}, inplace=True)
# Filtrando usuario por tempo de transmissão
#
user_by_time = (df_geral.drop_duplicates(subset='published_at').groupby(['user_name'])['duration'].sum()).to_frame()
user_by_time.rename(columns={'duration' : 'dur'}, inplace=True)
user_by_time = user_by_time['dur'].to_frame().reset_index()
user_by_time.rename(columns={'dur' : 'duration'}, inplace=True)
# Agrupamento de usuario por genero e tempo total de transmissão
user_by_gen_time = (df_geral.drop_duplicates(subset='published_at').groupby(['user_name','genre_name'])['duration'].sum()).to_frame()
user_by_gen_time.rename(columns={'duration' : 'dur'}, inplace=True)
user_by_gen_time = user_by_gen_time['dur'].to_frame().reset_index()
user_by_gen_time.rename(columns={'dur' : 'duration'}, inplace=True)

# Recomendação"""

# Dumificando o df de games
df_games_dum = pd.get_dummies(df_games,columns=['genre_name'])

# Escolher um streamer
streamers = list(set(df_geral['user_name'].to_list()))
with st.form("formulario"):
  streamer = st.selectbox(
      'Escolha seu streamer favorito',
      (streamers))
  st.write('Você escolheu:', streamer)
  submitted = st.form_submit_button("Escolher")
  if submitted:
    #jogos jogados pelo streamer em analise
    lista_jogos_analisados = list(set(df_geral[df_geral['user_name'] == streamer]['game_name']))

    df_game_score = df_games_dum[df_games_dum['game_name'].isin(lista_jogos_analisados)]
    df_game_score.loc['total'] = df_game_score.sum()

    # Pega os 2 generos com maior peso da lista
    genero_recomendado = [df_game_score.loc['total'].drop('game_name').sort_values(ascending=False).keys().to_list()[0]]
    genero_recomendado.append(df_game_score.loc['total'].drop('game_name').sort_values(ascending=False).keys().to_list()[1])

    # Cria uma lista com todos os jogos destes gêneros
    jogos_possiveis = list(set(df_games[df_games['genre_name'] == genero_recomendado[0][11:]]['game_name']))
    jogos_possiveis.append(list(set(df_games[df_games['genre_name'] == genero_recomendado[1][11:]]['game_name'])))

    # Jogos jogados pelo streamer escolhido
    games_jogados = df_geral[df_geral['user_name'] == streamer]['game_name'].value_counts().keys().to_list()

    # Remove os jogos já jogados pelo usuário
    for a in games_jogados:
      if a in jogos_possiveis:
        jogos_possiveis.remove(a)

    # Sugere aleatoriamente 10 jogos desta lista
    recomendados = []
    for a in range(10):
      escolha = random.randint(0,len(jogos_possiveis))
      recomendados.append(jogos_possiveis[escolha])

      ####
      ####
      ####
      # Cria DF com as colunas a serem exibidas
    df_games_consulta = pd.merge(df_games, df_game_streams, how='outer',on=['game_name'])

    # Renomeando colunas
    df_games_consulta.rename(columns={'genre_name' : 'Genero'}, inplace=True)
    df_games_consulta.rename(columns={'game_name' : 'Jogo'}, inplace=True)
    df_games_consulta.rename(columns={'streams' : 'Transmissões'}, inplace=True)

    #Ordenando colunas
    df_games_consulta = df_games_consulta[['Jogo','Genero','Transmissões']]

    # Completando os nulos
    df_games_consulta['Transmissões'].fillna(0, inplace=True)
    #
    #Exibindo recomendação de forma tabular
    try:
      for a in recomendados:
        st.write("Recomendamos :")
        st.write(str(a).capitalize())
        ajuste = df_games_consulta[df_games_consulta['Jogo'] == a].groupby(['Jogo','Genero'])['Transmissões'].value_counts().to_frame()
        ajuste.rename(columns={'Transmissões' : 'ajuste'},inplace=True)
        ajuste = ajuste['ajuste'].to_frame().reset_index()
        ajuste.rename(columns={'ajuste' : 'descarte'}, inplace=True)
        ajuste.drop(['descarte'],axis=1,inplace=True)
        df_selecao = ajuste
        st.write(df_selecao)
        print()
    except:
      st.write("Execute novamente")

