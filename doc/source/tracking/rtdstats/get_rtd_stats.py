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


# Turns out you cannot yet get the analytics data from the API, only the UI
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
# pageviews = fetch_rtd_analytics(
#     f"{base}/api/v3/projects/icepyx/", headers
# )
pageviews = pd.read_csv(trackpath + "pageview.csv")
exist_pageviews = pd.read_csv(trackpath + pageviewfn)

pageviews = pageviews.merge(
    exist_pageviews, how="outer", on=["Path", "Date", "Version", "Views"]
)

# remove duplicate entries; sort default is ascending
pageviews = pageviews.sort_values(["Date"], ignore_index=True).drop_duplicates(
    subset=["Date", "Version", "Path"], keep="last"
)

pageviews.sort_values(["Date"], ignore_index=True).to_csv(
    trackpath + pageviewfn, index=False
)

# see which pages have most views
pageviews.groupby("Path").sum().sort_values(["Views"], ascending=False)


# searches = fetch_rtd_analytics(f"{base}/api/v3/projects/icepyx/search-terms/", headers)

searches = pd.read_csv(trackpath + "searches.csv")
exist_searches = pd.read_csv(trackpath + searchfn)

searches = searches.merge(
    exist_searches, how="outer", on=["Created Date", "Query", "Total Results"]
)

searches.sort_values(["Query"], ignore_index=True).to_csv(
    trackpath + searchfn, index=False
)

# print out what most common query words are
searches.groupby("Query").count()
