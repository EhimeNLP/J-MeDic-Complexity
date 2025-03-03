# -*- coding: utf-8 -*-

import pandas as pd
import os
import pickle
import sys

def main(model, words, feature, output):
	df_feature = pd.read_csv(feature)
	df_words = pd.read_csv(words, header=None)

	with open(model, "rb") as f:
		model = pickle.load(f)
	
	pred = model.predict(df_feature)
	df_label = pd.DataFrame(pred)

	df_output = pd.concat([df_words, df_label], axis=1)
	df_output.columns = ["医療用語", "難易度"]

	df_output.to_csv(output, index=False, encoding="utf-8")

if __name__ == "__main__":
	cwd = os.getcwd()

	args = sys.argv
	INPUT_FILE = args[1]
	OUTPUT_FILE = args[2]
	MODEL_PATH = os.path.join(cwd, "../model/model.pkl")
	FEATURE_FILE = os.path.join(cwd, "../data/feature/all.csv")

	main(MODEL_PATH, INPUT_FILE, FEATURE_FILE, OUTPUT_FILE)