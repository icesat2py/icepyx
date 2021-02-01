import matplotlib.pyplot as plt
import pandas as pd
import os

trafficpath = "~/icepyx/doc/source/tracking/traffic/"
clonesfn = "clones.csv"
viewsfn = "views.csv"
defaultpath = "~/icepyx/traffic/"


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

fig.savefig("plots.png")

os.cmd("rm -rf " + defaultpath)
