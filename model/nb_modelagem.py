# -*- coding: utf-8 -*-
#Nb_modelagem.ipynb


# Grupo Games


##########################
# Importando bibliotecas #
##########################


import numpy as np
import pandas as pd
import datetime as dt
import random
import streamlit as st

##Puxando as bases de dados
st.write('Iniciando aplicação...')

df_geral = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_geral.csv')
df_games = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_games.csv')
df_game_streams = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_game_streams.csv')

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
        df_selecao = ajuste
        gens = df_selecao['Genero'][:].to_list()
        st.write('Generos:', *gens, sep=" ")
        st.write('Transmissões: ',df_selecao['Transmissões'][0])
        #st.write(df_selecao)
        st.write('\n\n')
    except:
      st.write("Execute novamente")

