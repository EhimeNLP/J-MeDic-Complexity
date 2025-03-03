import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

def concat_csv(dir, output):
    files = [
        'word_freq_sum_cc100_log.csv', 'word_freq_avg_cc100_log.csv', 
        'word_freq_max_cc100_log.csv', 'word_freq_min_cc100_log.csv',
        'char_freq_sum_cc100_log.csv', 'char_freq_avg_cc100_log.csv',
        'char_freq_max_cc100_log.csv', 'char_freq_min_cc100_log.csv',
        'char_freq_head_cc100_log.csv', 'char_freq_tail_cc100_log.csv',
        'word_freq_head_cc100_log.csv', 'word_freq_tail_cc100_log.csv',
        'word_freq_wiki_log.csv', 'word_freq_cc100_log.csv',
        'fasttext.csv',
        'char_type.csv', 'char_exist.csv', 'continuous_len.csv', 'split_len.csv',
        'word_freq_sum_wiki_log.csv', 'word_freq_avg_wiki_log.csv', 
        'word_freq_max_wiki_log.csv', 'word_freq_min_wiki_log.csv',
        'char_freq_sum_wiki_log.csv', 'char_freq_avg_wiki_log.csv',
        'char_freq_max_wiki_log.csv', 'char_freq_min_wiki_log.csv',
        'char_freq_head_wiki_log.csv', 'char_freq_tail_wiki_log.csv',
        'word_freq_head_wiki_log.csv', 'word_freq_tail_wiki_log.csv'
    ]

    dataframes = []
    
    for file in files:
        path = os.path.join(dir, file)
        if os.path.exists(path):
            df = pd.read_csv(path)
            dataframes.append(df)
        else:
            print(f"Warning: {file} not found and will be skipped.")

    if not dataframes:
        raise FileNotFoundError("No valid CSV files found in the directory.")

    df_vec = pd.concat(dataframes, axis=1)

    # 標準化
    std_scaler = StandardScaler()
    df_std = pd.DataFrame(std_scaler.fit_transform(df_vec), columns=df_vec.columns)

    df_std.to_csv(output, index=False)

def main():
    concat_csv(FEATURE_DIR, os.path.join(FEATURE_DIR, "all.csv"))

if __name__ == "__main__":
    cwd = os.getcwd()
    FEATURE_DIR = os.path.join(cwd, "../data/feature")
    main()