import os
import pypistats
import pandas as pd

cwd = os.getcwd()

trackpath = f"{cwd}/doc/source/tracking/pypistats/"
downloadfn = "downloads_data.csv"
sysdownloadfn = "sys_downloads_data.csv"

downloads = pypistats.overall("icepyx", total=True, format="pandas").drop(
    columns=["percent"]
)
downloads = downloads[downloads.category != "Total"]

# try:
exist_downloads = pd.read_csv(trackpath + downloadfn)  # .drop(columns=['percent'])
# exist_downloads = exist_downloads[exist_downloads.category != "Total"]
dl_data = downloads.merge(
    exist_downloads, how="outer", on=["category", "date", "downloads"]
)
# except:
#     dl_data = downloads

dl_data.sort_values(["category", "date"], ignore_index=True).to_csv(
    trackpath + downloadfn, index=False
)

sysdownloads = pypistats.system("icepyx", total=True, format="pandas").drop(
    columns=["percent"]
)
sysdownloads = sysdownloads[sysdownloads.category != "Total"]
# try:
exist_sysdownloads = pd.read_csv(
    trackpath + sysdownloadfn
)  # .drop(columns=['percent'])
# exist_sysdownloads = exist_sysdownloads[exist_sysdownloads.category != "Total"]
exist_sysdownloads["category"] = exist_sysdownloads["category"].fillna("null")
sysdl_data = sysdownloads.merge(
    exist_sysdownloads, how="outer", on=["category", "date", "downloads"]
)
# except:
#     dl_data = sysdownloads

sysdl_data.sort_values(["category", "date"], ignore_index=True).to_csv(
    trackpath + sysdownloadfn, index=False
)

dl_data = dl_data.groupby("category").get_group("without_mirrors").sort_values("date")

chart = dl_data.plot(
    x="date", y="downloads", figsize=(10, 2), label="Number of PyPI Downloads"
)
chart.figure.savefig(trackpath + "downloads.svg")
