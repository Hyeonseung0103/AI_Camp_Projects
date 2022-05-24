# install.packages("rJava")
# install.packages("multilinguer")
#multilinguer::install_jdk()
# 
# install.packages(c('stringr', 'hash', 'tau', 'Sejong', 'RSQLite', 'devtools'), type = "binary")
# install.packages("remotes")
# remotes::install_github('haven-jeon/KoNLP', upgrade = "never", INSTALL_opts=c("--no-multiarch"), force = T)

# Sys.getenv('R_LIBS_USER')
# fLib <- Sys.getenv('R_LIBS_USER')
# fLibScales <- paste0(fLib, '/Rcpp')
# unlink(fLibScales, recursive=TRUE)
# 
# install.packages('glue')
# install.packages('cli')
# install.packages("Rcpp")

install.packages("KoNLP")

library(rJava)
library(memoise)
library(multilinguer)
library(KoNLP)
## 패키지 불러오기
pkgs <- c(
  # Data munipulate packages   
  "dplyr",
  "stringr",
  
  # text mining packages
  "tidytext",
  "KoNLP",
  "tidyr",
  
  # graphic packages
  "ggplot2",
  
  'httr',
  'readr'
)

# 패키지 동시에 적용
sapply(pkgs, require, character.only = T)

# 감성사전 불러오기
useNIADic()

#KNU 감성사전
url = "https://drive.google.com/u/0/uc?id=14t6CqgzfNpJjU45W8HFmLBlHaI_FjOUw&export=download"
GET(url, write_disk(tf <- tempfile(fileext = ".csv")))

dic <- read_csv(tf)
rm(url,tf)

dim(dic)

# 긍정단어
dic %>% 
  filter(polarity == 2) %>% 
  arrange(word) %>% 
  head()

dim(dic)

write.csv(dic, file = 'KNU_Dict.csv')



#.libPaths("C:/Users/kim/Documents/R/win-library/3.6")
.libPaths("C:/Users/kim/Documents/R/win-library/4.0")
# .libPaths()
#install.packages('devtools')


####################
library(data.table)
library(dplyr)
library(stringi)
library(stringr)
library(KoNLP)
library(tibble)
library(tidytext)

setwd("C:/Users/kim/Desktop/2022/AI_camp/Section4/project/data")
dic <- read.table('KNU_Dict2.txt', sep = '\t', header = T)
dic %>% head()

raw_comment <- fread('fifa_comment_data2.csv', encoding = 'UTF-8')
raw_comment <- tibble(raw_comment$comment)
colnames(raw_comment) <- 'comment'
raw_comment %>% head()

# 댓글 데이터 전처리
fifa_comment <- raw_comment %>% 
  mutate(id = row_number(),
         reply = str_squish(comment))


fifa_comment %>% head()

# 데이터 토콘화 
word_comment <- fifa_comment %>% 
  unnest_tokens(input = reply,
                output = word,
                token = "words",
                drop = F)%>% 
  filter(str_detect(word, "[가-힣]")) %>%   
  filter(str_count(word) >= 2)

word_comment %>% 
  select(word, reply)

# 감정점수 부여
# 사전에 없는 단어는 모두 0(중립)으로 처리
word_comment <- word_comment %>% 
  left_join(dic, by ="word") %>% 
  mutate(polarity = ifelse(is.na(polarity), 0 , polarity))

# 감정 분류 하기 
word_comment <- word_comment %>% 
  mutate(sentiment = ifelse(polarity ==  2, "pos",
                            ifelse(polarity == -2, "neg", "neu")))

word_comment %>% head()

word_comment %>% 
  count(sentiment)

#댓글별 감정점수
score_comment <- word_comment %>% 
  group_by(id, reply) %>% 
  summarise(score = sum(polarity)) %>% 
  ungroup()


score_comment %>% 
  select(score, reply)

# 긍정 댓글 
score_comment %>% 
  select(score, reply) %>% 
  arrange(-score)

# 부정 댓글
score_comment %>% 
  select(score, reply) %>% 
  arrange(score) 

score_comment %>% head()
fifa_comment %>% head()


df <- fread('fifa_comment_data2.csv', encoding = 'UTF-8')
dim(df)
dim(score_comment)


df <- fifa_comment %>% 
  left_join(score_comment, by ="id") %>% 
  select(id,comment,score)
df[is.na(df$score),] %>% head(20)

dim(df)

origin <- fread('fifa_comment_data2.csv', encoding = 'UTF-8')
dim(origin)

df_score <- cbind(origin,df$score)
colnames(df_score)[6] <- 'score'

sum(is.na(df_score))
df_score[is.na(df_score$score),] %>% head(20)

df_score <- df_score[!is.na(df_score$score),]
sum(is.na(df_score))
dim(df_score)
df_score %>% head()


write.csv(df_score, file = 'sentiment_scores.csv', row.names = F)











