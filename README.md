# Sistema de recomendação de jogos para streamers da Twitch

Sistema de recomendação de jogos para streamers da Twitch
Esse artigo foi escrito como parte do projeto final do curso de Data Science & Machine Learning da Tera. Integrantes: Emmanuel Martins, Ítalo Ribeiro, Kamila Fernandes e Nilton Neto

## Contexto

Desde os primórdios da indústria do entretenimento interativo nos anos 50, os jogos eletrônicos vêm invadindo a vida das pessoas. Com o avanço da tecnologia, a popularização dos consoles de mesa e microcomputadores aumentou exponencialmente nos anos 90, dando início a muitas franquias multimilionárias e evidenciando a oportunidades desse novo nicho de mercado. Só em 2007 o lucro deste setor foi de US$9,5 bilhões, ultrapassando a indústria cinematográfica. E acelerada pela popularização dos smartphones nos últimos anos, hoje ultrapassa os US$200 bilhões, superando o mercado de filmes e música somados, com perspectivas de constante crescimento.

Com todo esse avanço, novas profissões vêm sendo criadas para atender as demandas de mercado. Atualmente a profissões de streamer é uma das mais fortes no momento. Só em 2020 as comunidades consumiram aproximadamente 30 milhões de horas de conteúdo[6].

A Twitch é atualmente uma das plataformas mais populares de streaming de jogos ao vivo, com cerca de 140 milhões de usuários e 1,86 bilhões de horas assistidas por mês.

Um criador de conteúdo geralmente busca expandir e consolidar o número de espectadores e assinantes de seu canal. Para isso é necessário que ele conheça seu público e adapte seu conteúdo a ele. Então vamos criar um algoritmo que faça indicações de jogos para os streamers da Twitch, baseado nos jogos já jogados anteriormente.

## Tudo começa pelo princípio: os dados

## Coleta

Dado que já sabemos o que queremos construir, para começar a desenhar o algoritmo, primeiro precisamos dos dados. Como nosso sistema de recomendação vai ser baseado em conteúdos já jogados anteriormente, precisamos desse histórico de jogos já jogados de cada um dos streamers.

A Twitch fornece uma API aberta em que podemos usá-la para obter os dados necessários.

A partir dos dados coletados pela API, conseguimos nosso primeiro dataset, que contém dados referentes ao streamer e às gravações de suas lives mais recentes, conhecidas como vods, e qual era o respectivo jogo desta live.

Observação importante: O jogo atribuído à essa vod é referente ao último jogo jogado pelo streamer, mesmo que esta pessoa tenha jogado outros jogos. Ou seja, se uma pessoa fez uma live de 4 horas e nesse tempo jogou 2 jogos diferentes, a vod inteira fica associada ao segundo jogo.

![alt text](https://miro.medium.com/max/1400/0*qK2eKTXdV-vkMPS1)

Dataframe obtido após consulta à api da Twitch
Além das informações dos streamers e seu histórico de jogos, também precisamos das informações referente aos jogos em si. Para coletar informações dos jogos, usamos a API do IGDB, um grande repositório de informações de jogos, similar ao IMDB para filmes e séries.

Com isso, temos nosso segundo dataset.

![alt text](https://miro.medium.com/max/640/0*M3puAa9FCl5bDc9d)

Dataframe obtido após consulta à api do IGDB

## Transformação dos datasets

Agora tendo as informações sobre os streamers, as vods da Twitch e sobre os jogos, precisamos juntar esses 2 datasets em um único e transformar seu formato para melhor uso na modelagem.

Primeiro, no dataset do IGDB, consideramos que as colunas theme_name e genre_name possuem o mesmo objetivo no nosso modelo: a propriedade de medir a semelhança entre os jogos.

Segundo, para juntar esses 2 datasets, não podemos depender das colunas game_id, porque elas são identificadores distintos entre cada origem de dados. Portanto, para juntá-los usaremos o nome do jogo formatado em minúsculo como chave do merge.

Após a junção dos datasets, criamos algumas features novas que definem melhor outras features existentes dos datasets originais.

Nós também decidimos ignorar categorias da Twitch que não dizem respeito a jogos, como Just Chatting, Cooking, Sleeping, etc. Vamos focar nos conteúdos voltados a jogos.

![alt text](https://miro.medium.com/max/720/0*fBtYO9bZK9-8R08F)

Dataframe resultante para análise e modelagem

## Análise dos Dados

Mesmo nosso modelo sendo algo simples, precisamos entender alguns pontos de comportamento das pessoas streamers da Twitch e dos jogos.

Primeiro, avaliamos quantos gêneros em média cada jogo tem associado. Isso interfere na capacidade do nosso modelo de entender a similaridade entre os jogos.

![alt text](https://miro.medium.com/max/640/0*9y7dgO6Z7mA1Liuu)

Quantidade de jogos por quantidade de gêneros associados

Pelo gráfico acima vemos que cada jogo tem em média de 3 a 6 gêneros associados.

Outro ponto interessante de olharmos é quantas pessoas (streamers) tem na base que jogam apenas 1 único jogo. Isso acontece porque vários streamers focam em ganharem recordes mundiais em um jogo específico, os chamados speedruns, ou então porque no período de tempo capturado essa pessoa só fez 1 stream na Twitch.

![alt text](https://miro.medium.com/max/640/0*D7J4UD4Pay3isZKr)

Quantidade de usuários por quantidade de jogos jogadas na Twitch
De acordo com o gráfico acima conseguimos ver que temos cerca de 70% dos usuários jogando apenas 1 jogo.

Como não conseguimos distinguir entre quem jogou por speedrun e quem só tem 1 live streamada nesse tempo do datasets, manteremos todos no modelo.

## Desenho da Solução

## Como um sistema de recomendação funciona?

Existem vários tipos de sistemas de recomendação (filtragem colaborativa, apriori de regras de associação, baseada em conteúdo, etc), mas vamos a recomendação baseada em conteúdo, que consiste em olhar para os itens já consumidos pelo usuário para recomendar itens similares.

Os motivos para escolhermos esse modelo foram:

+ É simples e tem baixo custo computacional;

Como iremos usar a aplicação gratuita do Streamlit Cloud, é importante nosso modelo ter um baixo custo operacional visto que não teremos servidores robustos disponíveis.

+ Podemos aproveitar o histórico existente da maior plataforma de live stream de jogos do mundo;
Em sistemas de recomendação, quanto mais informações sobre os usuários, melhor. Conseguimos consultar dados relevantes dos últimos 3 meses através da API da Twitch e obtemos um dataset bastante grande para podermos usar no modelo.

+ Não temos como obter feedbacks dos usuários;
Por definição, nós iremos criar um sistema de recomendação para os streamers, entretanto não temos temos acesso à todos os dados da Twitch, principalmente os que dizem respeito aos espectadores dos streamers (como contagem de views na hora em que o streamer está jogando aquele jogo), portanto não conseguiremos medir a relevância daquela recomendação para a qualidade do conteúdo do streamer.

+ Como partimos do princípio que o usuário já possui conta e vods existentes na twitch, não teremos a possibilidade de um cold start.
Por definição, iremos oferecer recomendações para streamers já cadastrados na plataforma e que já tenham pelo menos 1 vod de 30 minutos ou mais na plataforma.

## Como nosso modelo foi desenhado?
Para determinar a semelhança entre um jogo e outro iremos usar a feature de gênero dos jogos do dataset do IGDB (coluna genre_name).

Nosso modelo consiste em contar quais os top gêneros mais jogados pelo streamer e escolher aleatoriamente 10 jogos desses mesmos gêneros que não tenham sido jogados pelo streamer.

Não usamos uma biblioteca definida, nosso modelo foi escrito do zero o que nos dificulta na avaliação de métricas da qualidade dele. Por isso fizemos avaliações qualitativas baseadas em streamers que nós mesmos temos o costume de acompanhar.

Exemplo de avaliação em que o modelo fez boas recomendações
### BananaTrama

Exemplo de jogos que costuma jogar: Cult of the Lamb, Project Zomboid, Vampire Survivors, Fallout 4, The Binding of Isaac: Repentance.

Top 2 gêneros: Indie, Role Play Gaming (RPG)

Exemplo de jogos recomendados: Dark fantasy warriors, Ski Hard: Lorsbruck 1978, Red island, FootRock, Sand Bullets.

Nas recomendações realizadas o modelo conseguiu distinguir bem quais os gêneros de preferência e foi fácil selecionar jogos desses gêneros que fossem similares aos gostos e personalidade do streamer.

### Exemplo de avaliação em que o modelo não fez boas recomendações
DEUSDAGUERRARodrigo

Exemplos de jogos que costuma jogar: God of War II, God of War III, God of War Ragnarok, Dragon Ball Z: Kakarot, Resident Evil 4

Exemplos de jogos recomendados por nosso modelo: Bowmasters, Mickey Mouse, Farm under fire, Super mario bros galaxy ds, Mafia III

Essa avaliação mostra que o modelo poderia se beneficiar de melhorias para as recomendações além de apenas os top gêneros do streamer. As recomendações não seguem a personalidade do streamer ao trazer jogos para público mais infantil, mesmo que o streamer tenha um jogo “cartunesco” em seu repertório, que na verdade é um jogo de luta. Existe uma diferença que nós humanos conseguimos perceber entre jogos de luta temáticos e jogos infantis, mas que não conseguimos trazer ao modelo.

## E se continuássemos a melhorar o modelo, o que faríamos?
Trazer outras features que ajudariam o modelo a fazer seleções melhores, como:
+ Classificação indicativa;
+ Plataformas (não é todo mundo que tem um Nintendo Switch, por exemplo);
+ Feedbacks dos usuários

Testes dos hiperparâmetros
+ Usar os top 2 gêneros é suficiente?
+ Levar em consideração um tempo de histórico maior? Ou menor?

## Desafios e lições aprendidas
Uma boa definição de contexto e elaboração do problema faz toda a diferença na hora de definir a melhor solução possível;
Nós levamos meses para conseguir definir nosso contexto e escopo do projeto e, mesmo assim, mudamos várias vezes ao longo do curso.

Não podemos abraçar todos os problemas de uma vez só, precisamos escolher bem por onde começar. Simplificar o problema e a solução é um bom começo;
Nas primeiras definições de contexto e problemas, queríamos trazer uma ferramenta super personalizada e que trouxesse a resolução de vários problemas. Tivemos que reduzir drasticamente o escopo para conseguirmos focar em entregar uma ferramenta simples, mas com bom índice de qualidade.

A coleta de dados pode ser difícil se você não sabe onde eles estão, uma boa pesquisa é a chave se você depende de dados públicos na internet.
Tivemos sorte de encontrar uma plataforma que agregasse todas as informações de jogos em um só lugar e que fosse simples de acessar sua API e usar seus dados no projeto. Imagina se ela não existisse? Ou se não tivéssemos encontrado ela? Teríamos feito o trabalho de agregar os dados nós mesmos.
