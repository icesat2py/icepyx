# from github import Github
import matplotlib.pyplot as plt
import os
import pandas as pd
import subprocess


# print(os.environ)
# repo_name = os.environ["GITHUB_REPOSITORY"]
# github = Github(os.environ["TRAFFIC_ACTION_TOKEN"])
# # print("Repository name: ", repo_name)
# repo = github.get_repo(repo_name)


# defaultpath = "{}/{}".format(os.environ["GITHUB_WORKSPACE"], "traffic")
# print("Workplace path: ", defaultpath)

# # views_path = "{}/{}".format(workplace_path, "views.csv")
# # clones_path = "{}/{}".format(workplace_path, "clones.csv")
# # plots_path = "{}/{}".format(workplace_path, "plots.png")

# print(repo_name)
# print(os.environ["GITHUB_WORKSPACE"])
cwd = os.getcwd()

trafficpath = cwd + "/doc/source/tracking/traffic/"
clonesfn = "clones.csv"
viewsfn = "views.csv"
# defaultpath = "../../../../traffic/" #"~/traffic/"
defaultpath = "{}/{}/".format(cwd, "traffic")

def update_csv(fn, string):
    try:
        existing = pd.read_csv(trafficpath + fn)
        new = pd.read_csv(defaultpath + fn)
        updated = new.merge(
            existing, how="outer", on=["_date", "total_" + string, "unique_" + string]
        )
    except FileNotFoundError:
        updated = pd.read_csv(defaultpath + fn)

    updated.sort_values("_date", ignore_index=True).to_csv(
        trafficpath + fn, index=False
    )

    return updated


clones = update_csv(clonesfn, "clones")
views = update_csv(viewsfn, "views")

fig, ax = plt.subplots(figsize=(10, 4), nrows=2, ncols=1)

clones.sort_values("_date").plot(
    x="_date",
    y=["total_clones", "unique_clones"],
    label=["Total GitHub Clones", "Unique GitHub Clones"],
    ax=ax[0],
)

views.sort_values("_date").plot(
    x="_date",
    y=["total_views", "unique_views"],
    label=["Total GitHub Views", "Unique GitHub Views"],
    ax=ax[1],
)

fig.savefig(trafficpath + "plots.png")

subprocess.run(["rm -rf " + defaultpath[:-1]], shell=True)