## Assumptions that are different in Harmony

* We can't use short name and version with Harmony like we do with ECS, we have to use
  Concept ID (or DOI). We need to get this from CMR using short name and version.
* Variable subsetting won't be supported on day 1.
* All the ICESat-2 products we currently support will not be supported on day 1.
    * <https://nsidc.atlassian.net/wiki/spaces/DAACSW/pages/222593028/ICESat-2+data+sets+and+versions+we+are+supporting+for+Harmony>
* ECS and CMR shared some parameters. This is not the case with Harmony.


## Testing with Harmony

Harmony is available for testing in the UAT environment.

> [!NOTE]
> ICESat-2 products will be available in production in early October 2024. If you're
> reading this after that time, please talk to Amy Steiker about Harmony's current
> status before investing time setting up to test with UAT. If prod is available, test
> with prod.

We will need to interact with everything (CMR, Earthdata Login, Harmony itself) in UAT
for icepyx to work correctly.

* URLs *temporarily* modified for UAT.
* You need a separate Earthdata Login registration for UAT
  (<https://uat.urs.earthdata.nasa.gov/>).
* The UAT NSIDC provider name is `NSIDC_UAT`
  (<https://cmr.uat.earthdata.nasa.gov/search/collections.json?provider=NSIDC_CUAT>).
* To test in UAT (i.e. access data in `NSIDC_CUAT` provider), your Earthdata Login
  account must be on an access control list. Ask NSIDC operations for help.
    * The code *temporarily* uses `$EDL_TOKEN` envvar to authenticate with CMR. Populate
      this envvar with your Earthdata Login token.


## FAQ

### Which API?

Harmony has two APIs:

* [OGC Environmental Data Retrieval API](https://harmony.earthdata.nasa.gov/docs/edr-api)
* [OGC Coverages API](https://harmony.earthdata.nasa.gov/docs/api/)

Which should be used and when and why?


#### "Answer"

Use the [OGC Coverages API](https://harmony.earthdata.nasa.gov/docs/api/)!

> My take is that we ought to focus on the Coverages API for ICESat-2, since we aren’t
> making use of the new parameters. And this is what they primarily support. But I don’t
> have a good handle on whether we ought to pursue the EDR API at any point.
>
> - Amy Steiker

See this thread on EOSDIS Slack for more details:

<https://nsidc.slack.com/archives/CLC2SR1S6/p1716482829956969>
