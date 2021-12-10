import os
import json
import requests
from tqdm import tqdm
import random
import math
import numpy as np
from time import sleep
from util import get_star_cache, plot_score_against_star, scrape_stars

files = os.listdir("./data")
DO_FETCH = False
APPLY_FILTERS = False
repos = []

with open("./data/" + files[0]) as f:
    lines = f.readlines()
    repos.extend([json.loads(l) for l in lines])
print("# repos", len(repos))

random.seed(64)
random.shuffle(repos)

repos = repos[:27000]

if DO_FETCH:
    repos = scrape_stars(repos)

repo_stars = get_star_cache()
all_scores = [repo["score"] for repo in repos if repo_stars[repo["repo"]["name"]] <= 5000]
all_stars = [repo_stars[repo["repo"]["name"]] for repo in repos if repo_stars[repo["repo"]["name"]] <= 5000]

if APPLY_FILTERS:
    bucket_indexes = {}
    for i in tqdm(range(len(all_stars))):
        star_count = int(all_stars[i] / 1000)
        bucket_indexes[star_count] = bucket_indexes.get(star_count, []) + [i]


    sample_size = min([len(x) for x in bucket_indexes.values()])
    scores = []
    stars = []
    for bucket, indexes in bucket_indexes.items():
        index_sample = random.sample(indexes, sample_size)
        scores.extend([all_scores[i] for i in index_sample])
        stars.extend([all_stars[i] for i in index_sample])
else:
    scores = all_scores
    stars = all_stars

print(scores)
#print(stars)
print("RHO", np.corrcoef(scores, stars))

plot_score_against_star(scores, stars)
