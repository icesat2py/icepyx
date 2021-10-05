The following files may be part of this package.  Note that depending on the
search criteria used, some of these files may not be present because there
is no matching data.

CITATIONS.txt
  Information on sources for the data, as well as how to cite the data in
  your own works.

glims_hypsometry_*.csv
  Hypsometry (area-elevation histogram) data for the various glaciers/analyses
  in the search.  The data are provided in histogram form, with a different file
  for each bin size present in the database.  The CSV file has columns for the
  glacier ID and analysis ID, as well as a column for each elevation bin.
  The column header for each bin shows the center elevation of that bin.  The
  bins represent meters of elevation, and the   data represent the glacier area
  (in square kilometers) in that elevation bin.

  If there are no files present, there are no hypsometry data for any of the
  glaciers selected.

glims_images.*
  See FILE FORMATS below for details on the exact files included.  The files
  contain information on the images that are linked to the glaciers selected.
  Attributes include the glacier ID, analysis ID, instrument short name,
  original ID, acquisition time, and a flag called "est_loc".  If this flag
  is 0, it means the coordinates listed are what is stored in the database.
  If the flag is 1, it means no coordinates were given, so the coordinates
  listed were estimated as an average of the other image coordinates in the
  package.

  If this file is not present, there were no images corresponding to the
  glaciers selected.

glims_lines.*
  See FILE FORMATS below for details on the exact files included.  The data
  represent line features associated with the glaciers selected.  These line
  features will either be "snow lines" or "center lines" for the glacier.

  If this file is not present, there are no line data for the glaciers
  selected.

glims_points.*
  See FILE FORMATS below for details on the exact files included.  The data
  are representative points for the glaciers selected.

glims_polygons.*
  See FILE FORMATS below for details on the exact files included.  The data
  represent polygon features, typically glacier outlines, but also including
  regions of glacial lakes, debris cover, rocks within the glacier (nunataks),
  and other polygonal features.

README.txt
  This file.


------------
FILE FORMATS
------------
The exact nature of the files included for most of the files above depends on
the file format selected for the download.  This section describes the
expected files for each file format.  Here, glims_* refers to the file as
described above, such as "glims_images" or "glims_lines".


ESRI SHAPEFILE
  glims_*.dbf
    Attribute data and object IDs for the features
  glims_*.prj
    Definition of the map projection
  glims_*.shp
    Geometry information for the features
  glims_*.shx
    Geometry index to speed searching

MAPINFO TABLE
  glims_* directory, containing:
    layer.dat
      Attribute data for the features
    layer.id
      Info linking graphic data to the database
    layer.map
      Graphic and geographic information for each feature
    layer.tab
      ASCII file linking other files, holds information about the type of
      data set file

GML (Geographic Markup Language)
  glims_*.gml
    The main data file containing information on the features
  glims_*.xsd
    A schema file to describe the GML format.

KML (Keyhole Markup Language)
  glims_*.kml
    The main data file containing information on the features

GMT (Generic Mapping Tools; see http://gmt.soest.hawaii.edu/)
  glims_*.gmt
    The geometry, attribute, geographic extent, and projection data in a simple
    ASCII format defined by the GMT group
