# J-MeDic-Complexity
[万病辞書](https://sociocom.naist.jp/manbyou-dic/)に収録された医療用語に半自動的に用語難易度を付与しました。
|ラベル|内容|
|:---|:---|
|1（平易）|日常会話の中で使う|
|2|使ったことがある|
|3|意味が分かる|
|4|見た/聞いたことはあるが，意味は分からない|
|5（難解）|見た/聞いたことが無く，意味が分からない|

## ファイル情報
A列の出現形に対する用語難易度をB列に示しています。
|出現形（A列）|用語難易度（B列）|
| :--- | :---: |
|かぜ|1|
|眩暈症|2|
|上腕骨粉砕骨折|3|
|胆のう管癒着|4|
|仙腸関節ストレイン|5|

<br>

# 難易度辞書の更新
任意の医療用語に難易度を付与することもできます。

## 使い方
- [ここ](https://fasttext.cc/docs/en/crawl-vectors.html)からcc.ja.300.binをダウンロードし、[data/](./data/)に置く
- 難易度を推定したい医療用語をcsvファイルにまとめ、[data/words/](./data/words/)に置く（[sample.csv](./data/words/sample.csv)を参考にしてください）
- [code/bash.sh](./code/bash.sh)を実行する（ファイル名は適宜書き換えてください）
- [output/](./output/)に難易度が付与されたファイルが出力されます([output.csv](./output/output.csv)を参考にしてください)

<br>

# 文献情報
Soichiro Sugihara, Tomoyuki Kajiwara, Takashi Ninomiya, Shoko Wakamiya, Eiji Aramaki. <br>
Semi-automatic Construction of a Word Complexity Lexicon for Japanese Medical Terminology. <br>
Proceedings of the 6th Clinical Natural Language Processing Workshop, pp.329-333, Jun 2024. [[PDF](https://aclanthology.org/2024.clinicalnlp-1.29.pdf)]

<br>

# ライセンス
Creative Commons Attribution 4.0 International License (CC BY 4.0)
