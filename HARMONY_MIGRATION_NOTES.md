## Assumptions that are different in Harmony

* We can't use short name and version with Harmony like we do with ECS, we have to use
  Concept ID (or DOI). We need to get this from CMR using short name and version.
* Variable subsetting won't be supported on day 1.
* All the ICESat-2 products we currently support will not be supported on day 1.
    * <https://nsidc.atlassian.net/wiki/spaces/DAACSW/pages/222593028/ICESat-2+data+sets+and+versions+we+are+supporting+for+Harmony>
* ECS and CMR shared some parameters. This is not the case with Harmony.


## Getting started on development

### Work so far

Work in progress is on the `harmony` branch. This depends on the `low-hanging-refactors`
branch being merged. A PR is open.

> [!IMPORTANT]
> Several commits establish communication with UAT instead of production. They will need
> to be reverted once Harmony is available in prod.

In addition to this work, refactoring, type checking, and type annotations have been
added to the codebase to support the migration to Harmony.


### Familiarize with Harmony

* Check out this amazing notebook provided by Amy Steiker and Patrick Quinn:
  <https://github.com/nasa/harmony/blob/main/docs/Harmony%20API%20introduction.ipynb>
* Review the interactive API documentation:
  <https://harmony.uat.earthdata.nasa.gov/docs/api/> (remember, remove UAT from URL if
  Harmony is live with ICESat-2 products in early October 2024)


### Getting started replacing ECS with Harmony

1. Find the `WIP` commit (`ac916d6`) and use `git reset` to restore the changes into the
   working tree. There are several breakpoints set, as well as an artificially
   introduced exception class to help trace and narrow the code paths during
   refactoring.
2. Exercise a specific code path. For example:

    ```python
    import icepyx as ipx
    import datetime as dt

    q = ipx.Query(
        product="ATL06",
        version="006",
        spatial_extent=[-90, 68, 48, 90],
        # "./doc/source/example_notebooks/supporting_files/simple_test_poly.gpkg",
        date_range={
            "start_date": dt.datetime(2018, 10, 10, 0, 10, 0),
            "end_date": dt.datetime(2018, 10, 18, 14, 45, 30),
            # "end_date": '2019-02-28',
        }
    )

    q.download_granules("/tmp/icepyx")
    ```

3. Identify the first query to ECS. Queries, except the capabilities query in
   `is2ref.py`, are formed from constants in `urls.py`. Continue this practice. Harmony
   URLs in this file are placeholders.
4. Determine an equivalent Harmony query. The Harmony Coverages API has an equivalent to
   the capabilities query in `is2ref.py`, for example.
5. Raise `RefactoringException` at the top of any functions or methods which currently
   speak to ECS. This will help us find and delete those "dead code" functions later,
   and prevent them from being inadvertently executed.
6. Write new functions or methods which speak to Harmony instead. It's important to
   encapsulate the communication with the Harmony API in a single function. This may
   mean replacing one function with several smaller functions during refactoring.
7. Maintain the high standard of documentation in the code. Include examples as doctests
   in the new functions. Use Numpy style docstrings. **DO NOT** include type information
   in docstrings -- write type annotations instead. They will be automatically
   documented by the documentation generator.
8. Repeat from step 3 for the next EGI query.

### Watch out for broken assumptions

It's important to note that two major assumptions will require significant refactoring.
The type annotations will help with this process!

1. Broken assumption: "CMR and EGI share parameter sets". My mental model looks like:
  * Current: User passes in parameters to `Query(...)`. Those params are used to generate
    separate "CMR parameters" and "reqparams". "CMRparams" are spatial and temporal
    parameters compatible with CMR. I'm not sure about the naming of "reqparams", but I
    think of them as the EGI parameters (which may include more than the user passed, like
    `page_size`) _minus_ the CMR spatial and temporal parameters. The actual queries
    submitted to CMR and EGI are based on those generated parameter sets.
  * Future: In Harmony-land, the shared parameter assumption is broken. CMR and Harmony's
    Coverages API have completely parameter sets. The code can be drastically simplified:
    User passes in parameters to `Query(...)`. Those params are used directly to generate
    both CMR and Harmony queries without an intervening layer. E.g.
2. Broken assumption: "We can query with only short_name and version number". Harmony
   requires a unique identifier (concept ID or DOI). E.g.:
   <https://harmony.uat.earthdata.nasa.gov/capabilities?collectionId=C1261703129-EEDTEST>
   (NOTE: UAT query using a collection from a test provider; we should be using
   `NSIDC_CUAT` provider in real UAT queries and `NSIDC_CPRD` for real prod queries).
   Since we want the user to be able to provide short_name and version, implementing the
   concept ID as a `@cached_property` on `Query` which asks CMR for the concept ID makes
   sense to me.


### Don't forget to enhance along the way

* Now that we're ripping things apart and changing parameters, I think it's important to
  replace the TypedDict annotations we're using with Pydantic models. This will enable us
  to better encapsulate validation code that's currently spread around.


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


## Integrating with other ongoing Icepyx work

Harmony is a major breaking change, so we'll be releasing it in Icepyx v2. 

We know the community wants to break the API in some other ways, so we want to include those in v2 as well!

* Some of Icepyx's Query functionality is already served by earthaccess; refactor or replace the `Query` class?
* ?

Jessica is currently determining who can help work on these changes, and what that looks like. *If you, the 
Harmony/ECS migration developer, identify opportunities to easily replace portions of Icepyx with _earthaccess_
or other libraries, take advantage of that opportunity.

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
