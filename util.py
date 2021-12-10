
import requests
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
from multiprocessing import Pool
import matplotlib as mpl
import subprocess

# connect this to a mysql database
TOKENS = ["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", "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", "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"]
ACTIVE_TOKEN_INDEX = 0

checkTypeRisk = {
    "Maintained": "High",
    "Dependency-Update-Tool": "High",
    "Binary-Artifacts": "High",
    "Branch-Protection": "High",
    "Code-Review": "High",
    "Signed-Releases": "High",
    "Token-Permissions": "High",
    "Vulnerabilities": "High",
    "Fuzzing": "Medium",
    "Packaging": "Medium",
    "Pinned-Dependencies": "Medium",
    "SAST": "Medium",
    "Security-Policy": "Medium",
    "CI-Tests": "Low",
    "CII-Best-Practices": "Low",
    "Contributors": "Low"
}

checkTypeWeights = {
    "Critical": 10,
    "High": 7.5,
    "Medium": 5,
    "Low": 2.5
}

def read_star_cache():
    try:
        with open("./data/repo_stars.json") as f:
            repo_stars = json.load(f)
        for k, v in repo_stars.items():
            if v == -1:
                del repo_stars[k]
    except Exception as e:
        print("UNABLE TO FIND FILE:", e)
        repo_stars = {}
    return repo_stars

def write_star_cache(star_cache):
    with open("./data/repo_stars.json", "w") as f:
        json.dump(star_cache, f)

def fetch_stars(repo):
    global ACTIVE_TOKEN_INDEX
    repo_name = repo["repo"]["name"]
    url_parts = repo_name.split("/")
    handle = url_parts[1]
    name = url_parts[2]
    api_uri = f"https://api.github.com/repos/{handle}/{name}"
    
    token = TOKENS[ACTIVE_TOKEN_INDEX]
    res = requests.get(api_uri, headers={"Authorization" : "token " + token})
    body = json.loads(res.content)
    stars = body.get("stargazers_count", -1)
    if stars == -1 and "Not Found" not in body['message']:
        if "API rate limit" in body['message']:
            print("SWITHCING LIMIT")
            ACTIVE_TOKEN_INDEX = (ACTIVE_TOKEN_INDEX + 1) % len(TOKENS)
        print(res.content[:400])
    return stars

def scrape_stars(repos):
    n_fetched = 0
    batch_size = 1000
    star_cache = read_star_cache()
    print("initial star cache len:", len(star_cache))

    print("Initial # of repos:", len(repos))
    repos = [r for r in repos if r["repo"]["name"] not in star_cache]
    print("# of repos to fetch for:", len(repos))

    batches = [repos[i:i + batch_size] for i in range(0, len(repos), batch_size)]
    for batch in tqdm(batches):
        with Pool(4) as pool:
            stars = [x for x in tqdm(pool.imap(fetch_stars, batch), total=len(batch))]
        for i, repo in enumerate(batch):
            if stars[i] != -1:
                repo_name = repo["repo"]["name"]
                star_cache[repo_name] = stars[i]
        print("Size of star cache:", len(star_cache))
        write_star_cache(star_cache)
    return star_cache
            
            
def plot_score_against_star(scores, stars):
    plt.scatter(scores, stars)
    plt.title('Security scores vs. Github stars (N = ' + str(len(scores)) + ")")
    plt.ylabel('Github stars')
    plt.xlabel('Security score')
    plt.show()

def call_with_output(command):
    success = False
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, env={'GITHUB_AUTH_TOKEN': ",".join(TOKENS)}).decode()
        success = True
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    except Exception as e:
        # check_call can raise other exceptions, such as FileNotFoundError
        output = str(e)
    return success, output

def maybe_read_json_file(fname):
    try:
        with open(fname) as f:
            return json.load(f)
    except:
        return {}

def get_scorecard(repo_url):
    success, output = call_with_output(["./scorecard-linux-amd64", "--format", "json", "--repo=" + repo_url])
    if success:
        try:
            return True, json.loads(output)
        except:
            return False, output
    else:
        return False, output

def get_score(repo, apply_checks = []):
    score, total = 0,0
    reasons = []
    for check in repo["checks"]:
        checkType = check["name"]
        severity = checkTypeRisk[checkType]
        if checkType not in apply_checks or int(check["score"]) < 0:
            continue
        score += int(check["score"]) * checkTypeWeights[severity]
        total += checkTypeWeights[severity]
        reasons.append((checkType, check["reason"]))
    return score / total if total > 0 else None, reasons

def scale_plot_size(factor=1.5):
    default_dpi = mpl.rcParamsDefault['figure.dpi']
    mpl.rcParams['figure.dpi'] = default_dpi*factor


def view_reasons_behind_check(check_type, check_scores, score=-1):
    for repo, check_to_score in check_scores.items():
        if check_type in check_to_score and (score == -1 or check_to_score[check_type][0] == score):
            print(repo, check_to_score[check_type])

def set_plot_font_size(size):
    plt.rc('font', size=size) #controls default text size
    plt.rc('axes', titlesize=size) #fontsize of the title
    plt.rc('axes', labelsize=size) #fontsize of the x and y labels
    plt.rc('xtick', labelsize=size) #fontsize of the x tick labels
    plt.rc('ytick', labelsize=size) #fontsize of the y tick labels
    plt.rc('legend', fontsize=size) #fontsize of the legend

def show_cumulative_score_distribution(scorecards, title=""):
    plt.hist([s["score"] for s in scorecards])
    plt.xlim(0, 11)
    plt.xlabel("Score")
    plt.ylabel("# of repositories")
    plt.title(title)
    plt.show()

def show_distribution_by_check_type(repos, title=""):
    scale_plot_size()
    fig, ax = plt.subplots(4, 4)
    set_plot_font_size(7)
    plt.subplots_adjust(wspace=0.4, hspace=1)
    r, c = 0, 0
    check_scores = {}
    for check_type in tqdm(checkTypeRisk.keys()):
        scores, reasons = zip(*[get_score(repo, apply_checks=[check_type]) for repo in repos])
        valid_scores_and_repos = [(scores[i], repos[i]["repo"]["name"], reasons[i]) for i in range(len(scores)) if scores[i] is not None]
        for score, repo_name, reasons in valid_scores_and_repos:
            if repo_name not in check_scores:
                check_scores[repo_name] = {}
            check_scores[repo_name][check_type] = (score, reasons)

        valid_scores = [score for score, _, _ in valid_scores_and_repos]
        ax[r][c].hist(valid_scores)
        ax[r][c].set_title(check_type)
        ax[r][c].set_xlim(-1, 11)
        c = c + 1 if c < 3 else 0
        r = r + 1 if c == 0 else r
    plt.suptitle(title)
    fig.tight_layout()
    plt.show()
    return check_scores

def show_distribution_by_single_check(repos, check_type, title=""):
    scale_plot_size()
    check_scores = {}
    set_plot_font_size(10)
    scores, reasons = zip(*[get_score(repo, apply_checks=[check_type]) for repo in repos])
    valid_scores_and_repos = [(scores[i], repos[i]["repo"]["name"], reasons[i]) for i in range(len(scores)) if scores[i] is not None]
    for score, repo_name, reasons in tqdm(valid_scores_and_repos):
        if repo_name not in check_scores:
            check_scores[repo_name] = {}
        check_scores[repo_name][check_type] = (score, reasons)

    valid_scores = [score for score, _, _ in valid_scores_and_repos]
    plt.title(title)
    plt.hist(valid_scores)
    plt.xlim(-1, 11)
    plt.xlabel("Score")
    plt.ylabel("# of repositories")
    plt.show()
    return check_scores

def show_distribution_of_repo(repo_name, data):
    repo = next(x for x in data if x["repo"]["name"] == repo_name)
    return show_distribution_by_check_type([repo], title=repo_name)