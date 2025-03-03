# -*- coding: utf-8 -*-

import pandas as pd
import math
import collections
import json
import re
import fasttext
import MeCab
import numpy as np
import sys
import os
from pathlib import Path

def save_to_csv(df, filename):
    output_path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(output_path, index=False)

# 文字種ごとの文字数を数える
def count_char_types(words, patterns):
    count_type = []
    for word in words:
        count = [len(pattern.findall(word)) for pattern in patterns.values()]
        count_type.append(count)
    return pd.DataFrame(count_type, columns=patterns.keys())

# 文字種ごとの有無を判定
def check_char_existence(words, patterns):
    exist_char = []
    for word in words:
        exist = [1 if pattern.search(word) else 0 for pattern in patterns.values()]
        exist_char.append(exist)
    return pd.DataFrame(exist_char, columns=[f"{k}の有無" for k in patterns.keys()])

# 文字種ごとの連続数（最大値）を数える
def count_max_consecutive_chars(words, patterns):
    count_continue = []
    for word in words:
        count = []
        for pattern in patterns.values():
            matches = pattern.findall(word)
            if matches:
                max_len = max(len(match) for match in matches)
            else:
                max_len = 0
            count.append(max_len)
        count_continue.append(count)
    return pd.DataFrame(count_continue, columns=[f"{k}の連続数" for k in patterns.keys()])

# 構成素数
def count_constituent(words):
    tokenizer = MeCab.Tagger("-Owakati")
    split_len = []

    for word in words:
        tokens = tokenizer.parse(word).split()
        split_len.append(len(tokens))
    
    return pd.DataFrame(split_len, columns=["構成素数"])

# 単語長
def word_len(input_file):
    df = pd.read_csv(input_file, header=None, names=["医療用語"])
    df_len = pd.DataFrame(index=[], columns=["単語長"])
    df_len["単語長"] = df["医療用語"].apply(lambda x: len(x))

    return df_len

def freq_save_to_csv(data, filename, column_name):
    df = pd.DataFrame(data, columns=[column_name])
    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)

# 文字・単語頻度
def calculate_freq(cnt_dict, tokens, is_char_freq=True):
    freq_avg = []
    freq_min = []
    freq_max = []
    freq_sum = []
    freq_head = []
    freq_tail = []

    tokenizer = MeCab.Tagger("-Owakati")

    for line in tokens:
        if is_char_freq:
            tokens_list = list(line.rstrip())  # 文字単位
        else:
            tokens_list = tokenizer.parse(line.rstrip()).split()  # 単語単位
        
        cnt = 0
        min_ = float("inf")
        max_ = 0
        for token in tokens_list:
            cnt += cnt_dict[token]
            min_ = min(min_, cnt_dict[token])
            max_ = max(max_, cnt_dict[token])

        avg = cnt / len(tokens_list)
        freq_avg.append(avg)
        freq_min.append(min_)
        freq_max.append(max_)
        freq_sum.append(cnt)

        head = tokens_list[0]
        tail = tokens_list[-1]
        freq_head.append(cnt_dict[head])
        freq_tail.append(cnt_dict[tail])

    return freq_avg, freq_min, freq_max, freq_sum, freq_head, freq_tail

def general_freq(freq_json, med_list, out_avg, out_min, out_max, out_sum, out_head, out_tail, column_avg, column_min, column_max, column_sum, column_head, column_tail, is_char_freq=True):
    with open(freq_json, "r") as f:
        dict_ = json.load(f)
    
    cnt_dict = collections.Counter(dict_)
    
    with open(os.path.join(DATASET_DIR, med_list), "r") as f:
        tokens = f.readlines()
    
    # 頻度を計算する
    freq_avg, freq_min, freq_max, freq_sum, freq_head, freq_tail = calculate_freq(cnt_dict, tokens, is_char_freq)
    
    freq_save_to_csv(freq_avg, out_avg, column_avg)
    freq_save_to_csv(freq_min, out_min, column_min)
    freq_save_to_csv(freq_max, out_max, column_max)
    freq_save_to_csv(freq_sum, out_sum, column_sum)
    freq_save_to_csv(freq_head, out_head, column_head)
    freq_save_to_csv(freq_tail, out_tail, column_tail)

    # メモリ解放
    del cnt_dict
    del dict_

# 単語頻度(MeCab対応万病辞書を用いて、単語分割していない医療用語の頻度を数える)
def med_word_freq(freq_json, med_list, column, out):
    with open(freq_json, "r") as f:
        dict_ = json.load(f)

    cnt_dict = collections.Counter(dict_)
    
    freq = []
    
    with open(os.path.join(DATASET_DIR, med_list), "r") as f:
        for line in f:
            # 辞書に存在しない場合、デフォルト値（0）を返す
            token = line.rstrip()
            freq.append(cnt_dict.get(token, 0))
    
    freq_save_to_csv(freq, out, column)
    
    # メモリ解放
    del cnt_dict
    del dict_
    
#fasttext
def tokenize(medical_word):
    words = []
    tagger = MeCab.Tagger("-Owakati")
    for word in medical_word:
        words.append(tagger.parse(word).rstrip().split())
    return words

def vectorize(words, w2v):
    vectors = []
    for word in words:
        vectors.append(w2v[word])
    return np.array(vectors).mean(axis=0)

def create_vec(words, model):
    w2v = fasttext.load_model(model)
    vec = []
    for i in words:
        vec.append(vectorize(i, w2v))
    return pd.DataFrame(vec)

def to_log(input_csv, output_csv):
    df = pd.read_csv(os.path.join(OUTPUT_DIR, input_csv))
    df_log = df.applymap(lambda x: math.log(x) if isinstance(x, (int, float)) and x > 0 else x)
    df_log.to_csv(os.path.join(OUTPUT_DIR, output_csv), index=False)

def main():
    #医療用語をリストに格納
    words = list(pd.read_csv(WORDS, sep=",", encoding="utf-8", index_col=False, header=None)[0])
    
    patterns = {
        "ひらがな": re.compile("[ぁ-ゖ]"),
        "カタカナ": re.compile("[ァ-ヶー]"),
        "漢字": re.compile("[\u4E00-\u9FD0]"),
        "数字": re.compile("[0-9０-９]"),
        "アルファベット": re.compile("[a-zA-Zａ-ｚＡ-Ｚ]")
    }

    # 文字種ごとの文字数
    df_count = count_char_types(words, patterns)
    save_to_csv(df_count, "char_type.csv")

    # 文字種ごとの有無を判定
    df_count = check_char_existence(words, patterns)
    save_to_csv(df_count, "char_exist.csv")

    patterns2 = {
        "ひらがな": re.compile("[ぁ-ゖ]+"),
        "カタカナ": re.compile("[ァ-ヶー]+"),
        "漢字": re.compile("[\u4E00-\u9FD0]+"),
        "数字": re.compile("[0-9０-９]+"),
        "アルファベット": re.compile("[a-zA-Zａ-ｚＡ-Ｚ]+")
    }

    # 文字種ごとの連続数（最大値）
    df_consecutive = count_max_consecutive_chars(words, patterns2)
    save_to_csv(df_consecutive, "continuous_len.csv")

    # 構成素数
    df_constituent = count_constituent(words)
    save_to_csv(df_constituent, "split_len.csv")

    # 単語長
    df_word_len = word_len(os.path.join(DATASET_DIR, WORDS))
    save_to_csv(df_word_len, "word_len.csv")

    # 文字・単語頻度
    general_freq(os.path.join(DATASET_DIR, "split_char_wiki.json"), WORDS, 
                    "char_freq_avg_wiki.csv", "char_freq_min_wiki.csv", "char_freq_max_wiki.csv", "char_freq_sum_wiki.csv", 
                    "char_freq_head_wiki.csv", "char_freq_tail_wiki.csv", 
                    "文字頻度の平均(Wikipedia)", "文字頻度の最小値(Wikipedia)", "文字頻度の最大値(Wikipedia)", "文字頻度の総和(Wikipedia)", 
                    "先頭文字の頻度(Wikipedia)", "末尾文字の頻度(Wikipedia)", is_char_freq=True)
    general_freq(os.path.join(DATASET_DIR, "split_char_cc100.json"), WORDS, 
                        "char_freq_avg_cc100.csv", "char_freq_min_cc100.csv", "char_freq_max_cc100.csv", "char_freq_sum_cc100.csv", 
                        "char_freq_head_cc100.csv", "char_freq_tail_cc100.csv", 
                        "文字頻度の平均(CC100)", "文字頻度の最小値(CC100)", "文字頻度の最大値(CC100)", "文字頻度の総和(CC100)", 
                        "先頭文字の頻度(CC100)", "末尾文字の頻度(CC100)", is_char_freq=True)
    general_freq(os.path.join(DATASET_DIR, "wiki_freq_notmanbyo.json"), WORDS, 
                        "word_freq_avg_wiki.csv", "word_freq_min_wiki.csv", "word_freq_max_wiki.csv", "word_freq_sum_wiki.csv", 
                        "word_freq_head_wiki.csv", "word_freq_tail_wiki.csv", 
                        "単語頻度の平均(Wikipedia)", "単語頻度の最小値(Wikipedia)", "単語頻度の最大値(Wikipedia)", "単語頻度の総和(Wikipedia)", 
                        "先頭構成素の頻度(Wikipedia)", "末尾構成素の頻度(Wikipedia)", is_char_freq=False)
    general_freq(os.path.join(DATASET_DIR, "cc100_freq_notmanbyo.json"), WORDS, 
                        "word_freq_avg_cc100.csv", "word_freq_min_cc100.csv", "word_freq_max_cc100.csv", "word_freq_sum_cc100.csv", 
                        "word_freq_head_cc100.csv", "word_freq_tail_cc100.csv", 
                        "単語頻度の平均(CC100)", "単語頻度の最小値(CC100)", "単語頻度の最大値(CC100)", "単語頻度の総和(CC100)", 
                        "先頭構成素の頻度(CC100)", "末尾構成素の頻度(CC100)", is_char_freq=False)

    # 単語頻度(MeCab対応万病辞書を用いて、単語分割していない医療用語の頻度を数える)
    med_word_freq(os.path.join(DATASET_DIR, "cc100_freq.json"), WORDS, "単語頻度(CC100)", "word_freq_cc100.csv")
    med_word_freq(os.path.join(DATASET_DIR, "wiki_freq.json"), WORDS, "単語頻度(Wikipedia)", "word_freq_wiki.csv")

    tokenized_words = tokenize(words)
    fasttext_model = os.path.join(DATASET_DIR, "cc.ja.300.bin")
    df_fasttext = create_vec(tokenized_words, fasttext_model)
    save_to_csv(df_fasttext, "fasttext.csv")

    # ファイルリスト
    file_names = [
        "word_freq_sum_cc100.csv", "word_freq_avg_cc100.csv", "word_freq_max_cc100.csv", "word_freq_min_cc100.csv",
        "char_freq_sum_cc100.csv", "char_freq_avg_cc100.csv", "char_freq_max_cc100.csv", "char_freq_min_cc100.csv",
        "char_freq_head_cc100.csv", "char_freq_tail_cc100.csv", "word_freq_head_cc100.csv", "word_freq_tail_cc100.csv",
        "word_freq_cc100.csv", "word_freq_wiki.csv", "word_freq_sum_wiki.csv", "word_freq_avg_wiki.csv",
        "word_freq_max_wiki.csv", "word_freq_min_wiki.csv", "char_freq_sum_wiki.csv", "char_freq_avg_wiki.csv",
        "char_freq_max_wiki.csv", "char_freq_min_wiki.csv", "char_freq_head_wiki.csv", "char_freq_tail_wiki.csv",
        "word_freq_head_wiki.csv", "word_freq_tail_wiki.csv"
    ]

    # 変換処理
    for f in file_names:
        to_log(f, f.replace(".csv", "_log.csv"))

if __name__ == "__main__":
    cwd = os.getcwd()
    args = sys.argv
    WORDS = args[1]
    DATASET_DIR = os.path.join(cwd, "../data")
    OUTPUT_DIR = os.path.join(cwd, "../data/feature")

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    main()