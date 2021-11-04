import os
import subprocess
from tqdm import tqdm
from time import time, sleep
import json
from random import randint
from multiprocessing import Pool

def call_with_output(command):
    success = False
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        success = True
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    except Exception as e:
        # check_call can raise other exceptions, such as FileNotFoundError
        output = str(e)
    return success, output

def get_scorecard(repo_url):
    sleep(randint(3, 7))
    success, output = call_with_output(["./scorecard-linux-amd64", "--format", "json", "--repo=" + repo_url])
    try:
        scorecard = json.loads(output)
        return scorecard if success else None
    except:
        print(output)
        return None

def extract_repo_data(repo_data):
    return {
        "html_url": repo_data["html_url"],
        "stars": repo_data["stargazers_count"],
        "name": repo_data["full_name"],
        "id": repo_data["id"],
        "owner": repo_data["owner"]["login"]
    }


with open("repos.json") as f:
    raw_repos = json.load(f)
    repos = [extract_repo_data(r) for r in raw_repos]

scorecards = [get_scorecard(url) for url in tqdm([r["html_url"] for r in repos])]

for i in tqdm(range(len(repos))):
    scorecard = scorecards[i]
    repos[i]["score"] = scorecard["score"] if scorecard is not None else ""
    repos[i]["scorecard_result"] = scorecard

with open("scorecard-dataset.json", "w") as f:
    json.dump(repos, f, indent=2)






