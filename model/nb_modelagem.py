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
import time

##Puxando as bases de dados
with st.spinner('Carregando...'):
  df_geral = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_geral.csv')
  df_games = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_games.csv')
  df_game_streams = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_game_streams.csv')
  df_meta = pd.read_csv('https://raw.githubusercontent.com/emmanuelvrm/tera/main/data/df_games_rating.csv')

  # Recomendação"""

  # Dumificando o df de games
  df_meta = df_meta[['name','rating','storyline']]
  df_meta['rating'].fillna('Sem avaliação',inplace=True)
  df_meta['storyline'].fillna('Sem descrição',inplace=True)
  df_meta['name'] = df_meta['name'].str.lower()
  df_meta.rename(columns={'name': 'game_name'}, inplace = True)
  df_games= df_games.merge(df_meta,on='game_name')

  df_games_dum = pd.get_dummies(df_games,columns=['genre_name'])

  # Escolher um streamer
  streamers = list(set(df_geral['user_name'].to_list()))
st.success('Pronto!')


with st.form("formulario"):
  st.title('Recomendação de jogos baseado em VODs da Twitch')
  st.write('Bem-vindo!!!')
  st.write('Selecione seu streamer favorita da lista abaixo')
  st.write('Ainda não temos streamers gringos na lista, sorry :sweat_smile:')
  st.write('Iremos recomendar alguns jogos baseados nas suas vods salvas')
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
    genero_recomendado = [df_game_score.loc['total'].drop(['game_name','image_url','rating','storyline']).sort_values(ascending=False).keys().to_list()[0]]
    genero_recomendado.append(df_game_score.loc['total'].drop(['game_name','image_url','rating','storyline']).sort_values(ascending=False).keys().to_list()[1])

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
    df_games_consulta = df_games_consulta[['Jogo','Genero','Transmissões','image_url','rating','storyline']]

    # Completando os nulos
    df_games_consulta['Transmissões'].fillna(0, inplace=True)
    
    #Exibindo recomendação de forma tabular
    try:
      st.subheader("Recomendamos")
      st.markdown("""---""")
      for a in recomendados:
        col1, col2 = st.columns(2)
        ajuste = df_games_consulta[df_games_consulta['Jogo'] == a].groupby(['Jogo','Genero','image_url','rating','storyline'])['Transmissões'].value_counts().to_frame()
        ajuste.rename(columns={'Transmissões' : 'ajuste'},inplace=True)
        ajuste = ajuste['ajuste'].to_frame().reset_index()
        ajuste.rename(columns={'ajuste' : 'descarte'}, inplace=True)
        ajuste.drop(['descarte'],axis=1,inplace=True)
        df_selecao = ajuste
        df_selecao = ajuste
        gens = df_selecao['Genero'][:].to_list()
        with col1:
          st.subheader(str(a).capitalize())
          st.write('Generos:', *gens, sep=",")
          st.write('Transmissões: ',df_selecao['Transmissões'][0])
          st.write('Avaliação no IGDB: ',df_selecao['rating'][0])
          st.write('Descrição: ',df_selecao['storyline'][0])
          st.write('')
          
        with col2:
          st.image(df_selecao['image_url'][0])
          #st.write(df_selecao)
        st.markdown("""---""")
        st.write('\n\n')
      st.write("Criticas? Sugestões? Manda pra gente!")
      st.write("Emmanuel: https://www.linkedin.com/in/emmanuelvrm/")
      st.write("Italo: https://www.linkedin.com/in/italogsr/")
      st.write("Kamis: https://www.linkedin.com/in/kamila-fernandes/")
      st.write("Nilton: https://www.linkedin.com/in/nssiqueiraneto/")
    except:
      st.write("Execute novamente")