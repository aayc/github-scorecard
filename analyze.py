import json
with open("scorecard-dataset.json") as f:
    repos = json.load(f)

repos = [repo for repo in repos if repo["score"] != ""]
print("# repos: ", len(repos))

high_star_repos = [float(repo["score"]) for repo in repos if repo["is_high_stars"]]
high_star_avg_score = sum(high_star_repos)/len(high_star_repos)
low_star_repos = [(repo["score"]) for repo in repos if not repo["is_high_stars"]]
low_star_avg_score = sum(low_star_repos)/len(low_star_repos)
print("high average: ", high_star_avg_score)
print("low average: ", low_star_avg_score)

for repo in repos:
    print(repo["full_name"] + " " + str(repo["stars"]) + " " + str(repo["score"]))

