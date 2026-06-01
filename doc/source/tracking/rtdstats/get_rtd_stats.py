import os

import pandas as pd
import requests

cwd = os.getcwd()

trackpath = f"{cwd}/doc/source/tracking/rtdstats/"
pageviewfn = "pageview_data.csv"
searchfn = "searches_data.csv"

rtd_token = os.environ["RTD_API_TOKEN"]
headers = {"Authorization": f"Token {rtd_token}"}
base = "https://app.readthedocs.org"


def fetch_rtd_analytics(url, headers, output_path=None):
    """Fetch analytics from a Read the Docs URL and return a DataFrame."""
    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except Exception:
        return None

    if not resp.ok:
        return None

    try:
        data = resp.json()
    except Exception:
        return None

    if isinstance(data, dict) and "results" in data:
        results = data.get("results", [])
        if results:
            df = pd.json_normalize(results)
            if output_path:
                df.to_csv(output_path, index=False)
            return df
        return None

    if isinstance(data, list):
        df = pd.json_normalize(data)
        if output_path:
            df.to_csv(output_path, index=False)
        return df

    return None


### WIP to collect the analytics data and combine it with whatever already exists
pageviews = fetch_rtd_analytics(
    f"{base}/api/v3/projects/icepyx/search-analytics/", headers
)
exist_pageviews = pd.read_csv(trackpath + pageviewfn)

pageviews = pageviews.merge(
    exist_pageviews, how="outer", on=["category", "date", "downloads"]
)

pageviews.sort_values(["category", "date"], ignore_index=True).to_csv(
    trackpath + pageviewfn, index=False
)


searches = fetch_rtd_analytics(f"{base}/api/v3/projects/icepyx/search-terms/", headers)
exist_searches = pd.read_csv(trackpath + searchfn)

searches = searches.merge(
    exist_searches, how="outer", on=["category", "date", "downloads"]
)

searches.sort_values(["category", "date"], ignore_index=True).to_csv(
    trackpath + searchfn, index=False
)


### create some sort of summary info (e.g. cumulative/last 3 months most viewed page?)

# dl_data = dl_data.groupby("category").get_group("without_mirrors").sort_values("date")

# chart = dl_data.plot(
#     x="date", y="downloads", figsize=(10, 2), label="Number of PyPI Downloads"
# )
# chart.figure.savefig(trackpath + "downloads.svg")
