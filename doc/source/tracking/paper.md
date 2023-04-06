---
title: 'icepyx: querying, obtaining, analyzing, and manipulating ICESat-2 datasets'
tags:
  - Python
  - ICESat-2
  - LiDAR
  - elevation
  - community
  - cloud

authors:
  - name: Jessica Scheick^[Corresponding author] # note this makes a footnote
    orcid: 0000-0002-3421-4459
    affiliation: 1
  - name: Wei Ji Leong
    orcid: 0000-0003-2354-1988
    affiliation: 2
  - name: Kelsey Bisson
    orcid: 0000-0003-4230-3467
    affiliation: 3
  - name: Anthony Arendt
    orcid: 0000-0003-0429-6905
    affiliation: 4
  - name: Shashank Bhushan
    orcid: 0000-0003-3712-996X
    affiliation: 4
  - name: Zachary Fair
    orcid: 0000-0002-6047-1723
    affiliation: 5
  - name: Norland Raphael Hagen
    orcid: 0000-0003-1994-1153
    affiliation: 6
  - name: Scott Henderson
    orcid: 0000-0003-0624-4965
    affiliation: 4
  - name: Friedrich Knuth
    orcid: 0000-0003-1645-1984
    affiliation: 4
  - name: Tian Li
    orcid: 0000-0002-1577-4004
    affiliation: 7
  - name: Zheng Liu
    orcid: 0000-0003-4132-8136
    affiliation: 4
  - name: Romina Piunno
    orcid: 0009-0000-1144-0915
    affiliation: 8
  - name: Nitin Ravinder
    affiliation: 9
  - name: Landung "Don" Setiawan
    orcid: 0000-0002-1624-2667
    affiliation: 4
  - name: Tyler Sutterley
    orcid: 0000-0002-6964-1194
    affiliation: 4
  - name: JP Swinski
    affiliation: 5
  - name: Anubhav
    orcid: 0000-0003-4017-2862
    affiliation: 10

# Note: first three authors are driving the publication. Additional contributors/authors are listed in alphabetical order by last name. Anyone who also contributes substantially to preparing the JOSS submission will be moved into ABC order after the first three and before the "non-publication" contributors to icepyx. Non-responsive coauthors will be removed from the list since their permission to be included was not granted.

affiliations:
 - name: University of New Hampshire, USA
   index: 1
 - name: Development Seed, USA
   index: 2
 - name: Oregon State University, USA
   index: 3
 - name: University of Washington, USA
   index: 4
 - name: NASA Goddard Space Flight Center, USA
   index: 5
 - name: CarbonPlan, USA
   index: 6
 - name: University of Bristol, UK
   index: 7
 - name: University of Toronto, Canada
   index: 8
 - name: University of Leeds, UK
   index: 9
 - name: University of Maryland, College Park, USA
   index: 10
date: 23 September 2022
bibliography: icepyx_pubs.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi:
aas-journal:
---

# Summary

icepyx is both a software library and a community composed of ICESat-2 (NASA satellite) data users, developers, maintainers, and the scientific community.
We are working together to develop a shared library of resources - including existing resources, new code, tutorials, and use-cases/examples - that simplify the process of querying, obtaining, analyzing, and manipulating ICESat-2 datasets to enable scientific discovery.

# Statement of need

icepyx aims to provide a clearinghouse for code, functionality to improve interoperability, documentation, examples, and educational resources that tackle disciplinary research questions while minimizing the amount of repeated effort across groups utilizing similar datasets.
icepyx also hopes to foster collaboration, open-science practices, and reproducible workflows by integrating and sharing resources.

The Ice, Cloud, and Land Elevation Satellite-2 (ICESat-2) [@is2] was launched by NASA in September 2018.
The laser altimeter on board the satellite emits green light to the Earth's surface and measures the time until each pulse is returned to the satellite's sensors.
This information is used to determine the surface height of the land, ice, snow, trees, water, clouds, etc. that the satellite is passing over.
The instrument provides close to 500 GB of data per day, allowing scientists to investigate the surface height of earth's features in unprecedented detail.

icepyx began during the cryosphere-themed ICESat-2 Hackweek at the University of Washington in June 2019.
At the event, there was a clear need for a collaborative, shared community space that combined and generalized the tools and materials written by past, present, and future Hackweek participants, ICESat-2 Science Team members, and the data user community.
A unified framework of code and documentated examples for downloading, reading, and visualizing ICESat-2 data that is well tested makes it more accessible for everyone to use.
The library and community continue to grow and evolve, adding new features and building scientific literacy in open-science, cloud computing, and collaborative development best practices.

icepyx is now a foundational tool for accessing and working with ICESat-2 data, responsible for nearly a quarter of all NASA data center granule downloads in 2022. The library is complemented by a series of other specialized tools for interacting with and obtaining ICESat-2 data. These include OpenAltimetry[@OA], a browser based web tool to visualize and download selected ICESat and ICESat-2 surface heights, SlideRule[@SR], a server-side framework to create cloud-based, on-demand customized data processing for ICESat-2 data, and multiple product-focused tools for scientific data analysis (e.g. PhoREAL, PhotonLabeler). These tools are described in more detail in the icepyx documentation's [ICESat-2 Resource Guide](https://icepyx.readthedocs.io/en/latest/community/resources.html).

icepyx is also featured in multiple scientific publications [@Bisson:2021; @Fernando:2021; @Li:2020], presentations [@js2021agu; @js2020agu; @js2019agu], and educational events/Hackweeks [@2022_IS2-HW-tutorials; @2020_IS2-HW-tutorials].

# Acknowledgements

We acknowledge funding support from NASA and the University of Washington eScience Institute.
Anthony Arendt, Fernando Perez, Lindsey Heagey, and the Pangeo team provided invaluable support and guidance in establishing this library and welcoming us to the open-source community.
Amy Steiker, Mikala Beig, Nick Kotlinski, Luis Lopez, and many others at the National Snow and Ice Data Center (NSIDC) provide technical support and data access guidance.
The icepyx contributors list also includes many wonderful folks who shared ideas, provided mentoring, embraced the opportunity to engage in open-science practices while working with ICESat-2 data products, and contributed to icepyx.

<!-- Acknowledgments (non-responsive-potential-author contributors)
  - name: Sarah Hall
    affiliation: 1
  - name: Tom Johnson
    affiliation: 6
  - name: Luis Lopez
    affiliation: 9

  - name: Trey Stafford
    affiliation: 9
  - name: Amy Steiker
    affiliation: 9
  - name: Bruce Wallin
    affiliation: 9
-->

<!-- Acknowledgments (non-author contributors)
Nicole Abib
Sebastian Alvis
Mikala Beig
Alex DiBella
Nick K
Ted Maksym
Joachim Meyer
Fernando Perez
Facu Sapienza
David Shean
Trevor Skaggs
Ben Smith
Rachel Tilling
Anna Valentine
Molly Wieringa
Bidhya -->


# References
