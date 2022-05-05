---
title: 'icepyx'
tags:
  - Python
  - ICESat-2
  - data access
  - LiDAR
  - elevation
  - community
authors:
  - name: Jessica Scheick^[Corresponding author] # note this makes a footnote
    orcid: 0000-0000-0000-0000
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Wei Ji Leong
    affiliation: 2
  - name: Kelsey Bisson
    affiliation: 3
  - name: 
    affiliation: 3
  - name: 
    affiliation: 3
  - name: 
    affiliation: 3
  - name: 
    affiliation: 3
  - name: 
    affiliation: 3

Note: first three authors are driving the publication. Additional contributors/authors are listed in alphabetical order by last name. Anyone who also contributes to reviewing the JOSS submission will be moved into ABC order after the first three and before the non-publication contributors to icepyx.

Jessica Scheick
Wei Ji Leong
Kelsey Bisson

Anthony Arendt
Shashank B
Zach Fair
Raphael Hagen
Scott Henderson
Friedrich Knuth
Tian Li
Zheng Liu
Romina Piunno
Facu Sapienza
Landung "Don" Setiawan
Trey Stafford
Amy Steiker
Tyler Sutterley
Bruce Wallin
Learn2Pheonix






  
affiliations:
 - name: University of New Hampshire, USA
   index: 1
 - name: Institution Name, Country
   index: 2
 - name: Independent Researcher, Country
   index: 3
date: 18 April 2022
bibliography: icepyx_pubs.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi: 
aas-journal: 
---

# Summary

icepyx is both a software library and a community composed of ICESat-2 data users, developers, and the scientific community.
We are working together to develop a shared library of resources - including existing resources, new code, tutorials, and use-cases/examples - that simplify the process of querying, obtaining, analyzing, and manipulating ICESat-2 datasets to enable scientific discovery.

# Statement of need

icepyx aims to provide a clearinghouse for code, functionality to improve interoperability, documentation, examples, and educational resources that tackle disciplinary research questions while minimizing the amount of repeated effort across groups utilizing similar datasets. icepyx also hopes to foster collaboration, open-science, and reproducible workflows by integrating and sharing resources.

Many of the underlying tools from which icepyx was developed began as Jupyter Notebooks developed for and during the cryosphere-themed ICESat-2 Hackweek at the University of Washington in June 2019 or as scripts written and used by the ICESat-2 Science Team members. This project combines and generalizes these scripts into a unified framework, adding examples, documentation, and testing where necessary and making them accessible for everyone. It also improves interoperability for ICESat-2 datasets with other open-source tools. Our resources guide provides additional information on both the foundational documents for icepyx and closely related libraries for working with ICESat-2 data.

(Example text)
`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

Figures to include: icepyx in context of other tools

# Acknowledgements

We acknowledge funding support from NASA and the University of Washington eScience Institute.
Anthony Arendt, Fernando Perez, Lindsey Heagey, and the Pangeo team provided invaluable support and guidance in establishing this library and welcoming us to the open-source community.
Amy Steiker, Mikala Beig, Nick Kotlinski, Luis Lopez, and many others at the National Snow and Ice Data Center (NSIDC) provide technical support and data access guidance.
The icepyx contributors list also includes many Hackweek planners and participants who shared ideas and embraced the opportunity to engage in open-science practices.

<!-- Acknowledgments
Mikala Beig
Alex DiBella 
Tom Johnson
Nick K
Luis Lopez
Fernando Perez
David Shean
Rachel Tilling
Anna Valentine
Bidhya -->


# References