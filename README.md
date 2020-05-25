# Yet Another Power System Model (YAPOS)

**What is YAPOS?** YAPOS is an economic dispatch model implemented in
Python using [Pyomo](www.pyomo.org). The problem is defined at daily
time-scale and it aims to provide a simple, yet insightful, modelisation
of national power systems.

**Why another power system model?** Although several sophisticated power
system model already exist with open license (for example
[Dispa-SET](http://www.dispaset.eu), [PyPSA](https://www.pypsa.org/)),
YAPOS provides an alternative to all the users that:

1.  Do not want or cannot use a commercial solver (e.g. GUROBI or CPLEX)
2.  Want something light to run (a simulation for 34 countries run in a
    couple of minutes)
3.  Need a tool able to run many simulations in batch in a tidy way

**How to use YAPOS?** YAPOS has been developed and designed aiming to
build an impact model for all the people investigating the link between
energy & meteorology. However, it can be used whenever you need a
lightweight power system model able to reproduce the impact of
meteorological factors.

## Installation

YAPOS consists of a single Python file which requires the following
modules: - pyomo - numpy - pandas - xarray with netcdf4

You can install manually the modules with `pip` or other package
managers. If you use anaconda you can easily create an environment for
YAPOS with the following command: `conda env create -f environment.yml`

## Getting started

From you Python environment you can run a test simulation with the
command: `python main.py db/test/ test_run`

The output of the simulation can be found in the folder `db/test`.

With YAPOS code you can also find a database of simulations already
available. [More information here](#simulations).

## Notes and caveats

  - The model uses [Cbc solver](https://projects.coin-or.org/Cbc) as
    default solver, however the code might be easily adapted to use
    other solvers (e.g. GLPK)
  - The model interprets the input files in a “positional” fashion
    because our formulation converts the CSVs into information by
    position (using Pandas `iloc`). Then be careful when changing the
    inputs, all the dimensions (units, zones, etc.) MUST follow the same
    order in all the input files.

## How to set up and launch a simulation

1.  Create a folder for each simulation
2.  Copy inside the folder the input files needed for the simulation

<!-- end list -->

  - Generation units: `gen.csv`
  - Transmission lines: `lin.csv`
  - Demand time-series: `dem.csv`
  - Renewable time-series: `ren.csv`
  - Inflow time-series: `inflow.csv`
  - Availability time-series: `avail.csv`
  - Minimum storage levels: `stomin.csv`

<!-- end list -->

3.  Run the model with Python

#### R package

A companion package written in R named `yaposer` will be available soon.
The package will help the user to load, save, edit and visualisize
simulation inputs and results.

## Formulation

YAPOS uses a linear formulation at daily resolution. There are seven
continuous variables (and three slack variables) defined over four sets.

| Name |    Description     |
| :--: | :----------------: |
| `g`  |  Generation units  |
| `l`  | Tranmissions lines |
| `n`  |  Simulation zones  |
| `t`  |     Time steps     |

Sets

|       Name       |                  Description                  |
| :--------------: | :-------------------------------------------: |
| `system_cost(t)` |                  System cost                  |
|   `prod(g,t)`    | Electricity production for the unit `g` (MWh) |
|    `sl(g,t)`     |     Storage level for the unit `g` (MWh)      |
|     `u(g,t)`     |    Commitment level for the unit `g` (0-1)    |
|    `shd(n,t)`    |        Shed load in the zone `n` (MWh)        |
|   `curt(n,t)`    |  Curtailed electricity in the zone `n` (MWh)  |
|    `flw(l,t)`    |    Electricity flow on the line `l` (MWh)     |

Optimization
variables

| Name                 | Description                                                     |
| :------------------- | :-------------------------------------------------------------- |
| `water_slack(g,t)`   | Slack for the storage balance constraint                        |
| `storage_slack(g,t)` | Slack for the constraint on the minimum storage                 |
| `curt_slack(n,t)`    | Slack for the constraint on the maximum curtailable electricity |

Slack variables

The optimization problem uses the following objective
function:

\[\sum_{g,t} COST(g) \cdot prod(g,t) + \sum_{n,t} 400 \cdot shd(n,t) + \sum_{g,t} 100 \cdot water\_slack(g,t) + \sum_{g,t} 100 \cdot storage\_slack(g,t) + \sum_{n,t} 100 \cdot curt\_slack(n,t) \]

The formulation uses 13 different constraints:

  - Electricity balance
  - Minimum generation for the units
  - Maximum generation for the units
  - Maximum rate of ramping-up for hydropower
  - Maximum rate of ramping-down for hydropower
  - Minimum storage level
  - Maximum storage level
  - Storage balance
  - Maximum discharge for hydropower
  - Minimum power flow
  - Maximum power flow

## Inputs

As explained [before](#setup) YAPOS needs seven input files.

### Demand

File name is `dem.csv` and contains a time-series per zone of the
electricity demand. <!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#xbyagpcmfl .gt_table {
  display: table;
  border-collapse: collapse;
  margin-left: auto;
  margin-right: auto;
  color: #333333;
  font-size: smaller;
  background-color: #FFFFFF;
  width: auto;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #A8A8A8;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #A8A8A8;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
}

#xbyagpcmfl .gt_heading {
  background-color: #FFFFFF;
  text-align: center;
  border-bottom-color: #FFFFFF;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
}

#xbyagpcmfl .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#xbyagpcmfl .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#xbyagpcmfl .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#xbyagpcmfl .gt_col_headings {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
}

#xbyagpcmfl .gt_col_heading {
  color: #333333;
  background-color: #FFFFFF;
  font-size: smaller;
  font-weight: bold;
  text-transform: inherit;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: bottom;
  padding-top: 5px;
  padding-bottom: 6px;
  padding-left: 5px;
  padding-right: 5px;
  overflow-x: hidden;
}

#xbyagpcmfl .gt_column_spanner_outer {
  color: #333333;
  background-color: #FFFFFF;
  font-size: smaller;
  font-weight: bold;
  text-transform: inherit;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 4px;
  padding-right: 4px;
}

#xbyagpcmfl .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#xbyagpcmfl .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#xbyagpcmfl .gt_column_spanner {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  vertical-align: bottom;
  padding-top: 5px;
  padding-bottom: 6px;
  overflow-x: hidden;
  display: inline-block;
  width: 100%;
}

#xbyagpcmfl .gt_group_heading {
  padding: 8px;
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  text-transform: inherit;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: middle;
}

#xbyagpcmfl .gt_empty_group_heading {
  padding: 0.5px;
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  vertical-align: middle;
}

#xbyagpcmfl .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#xbyagpcmfl .gt_from_md > :first-child {
  margin-top: 0;
}

#xbyagpcmfl .gt_from_md > :last-child {
  margin-bottom: 0;
}

#xbyagpcmfl .gt_row {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 5px;
  padding-right: 5px;
  margin: 10px;
  border-top-style: solid;
  border-top-width: 1px;
  border-top-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: middle;
  overflow-x: hidden;
}

#xbyagpcmfl .gt_stub {
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  text-transform: inherit;
  border-right-style: solid;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
  padding-left: 12px;
}

#xbyagpcmfl .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#xbyagpcmfl .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#xbyagpcmfl .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#xbyagpcmfl .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#xbyagpcmfl .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#xbyagpcmfl .gt_footnotes {
  color: #333333;
  background-color: #FFFFFF;
  border-bottom-style: none;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
}

#xbyagpcmfl .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#xbyagpcmfl .gt_sourcenotes {
  color: #333333;
  background-color: #FFFFFF;
  border-bottom-style: none;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
}

#xbyagpcmfl .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#xbyagpcmfl .gt_left {
  text-align: left;
}

#xbyagpcmfl .gt_center {
  text-align: center;
}

#xbyagpcmfl .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#xbyagpcmfl .gt_font_normal {
  font-weight: normal;
}

#xbyagpcmfl .gt_font_bold {
  font-weight: bold;
}

#xbyagpcmfl .gt_font_italic {
  font-style: italic;
}

#xbyagpcmfl .gt_super {
  font-size: 65%;
}

#xbyagpcmfl .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="xbyagpcmfl" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="28" class="gt_heading gt_title gt_font_normal" style>

<strong>Daily
demand</strong>

</th>

</tr>

<tr>

<th colspan="28" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First three
days

</th>

</tr>

</thead>

<thead class="gt_col_headings">

<tr>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR

</th>

</tr>

</thead>

<tbody class="gt_table_body">

<tr>

<td class="gt_row gt_right">

292,467

</td>

<td class="gt_row gt_right">

210,703

</td>

<td class="gt_row gt_right">

1,556,073

</td>

<td class="gt_row gt_right">

1,170,710

</td>

<td class="gt_row gt_right">

92,694

</td>

<td class="gt_row gt_right">

578,629

</td>

<td class="gt_row gt_right">

111,416

</td>

<td class="gt_row gt_right">

175,029

</td>

<td class="gt_row gt_right">

632,214

</td>

<td class="gt_row gt_right">

1,019,288

</td>

<td class="gt_row gt_right">

70,998

</td>

<td class="gt_row gt_right">

473,592

</td>

<td class="gt_row gt_right">

461,015

</td>

<td class="gt_row gt_right">

254,082

</td>

<td class="gt_row gt_right">

344,699

</td>

<td class="gt_row gt_right">

170,765

</td>

<td class="gt_row gt_right">

27,211

</td>

<td class="gt_row gt_right">

19,103

</td>

<td class="gt_row gt_right">

23,523

</td>

<td class="gt_row gt_right">

163,429

</td>

<td class="gt_row gt_right">

96,521

</td>

<td class="gt_row gt_right">

144,119

</td>

<td class="gt_row gt_right">

66,929

</td>

<td class="gt_row gt_right">

31,191

</td>

<td class="gt_row gt_right">

88,687

</td>

<td class="gt_row gt_right">

40,617

</td>

<td class="gt_row gt_right">

156,689

</td>

<td class="gt_row gt_right">

117,336

</td>

</tr>

<tr>

<td class="gt_row gt_right">

328,015

</td>

<td class="gt_row gt_right">

244,574

</td>

<td class="gt_row gt_right">

1,720,765

</td>

<td class="gt_row gt_right">

1,392,108

</td>

<td class="gt_row gt_right">

96,407

</td>

<td class="gt_row gt_right">

706,866

</td>

<td class="gt_row gt_right">

136,122

</td>

<td class="gt_row gt_right">

201,807

</td>

<td class="gt_row gt_right">

762,106

</td>

<td class="gt_row gt_right">

985,103

</td>

<td class="gt_row gt_right">

73,619

</td>

<td class="gt_row gt_right">

468,065

</td>

<td class="gt_row gt_right">

489,230

</td>

<td class="gt_row gt_right">

279,589

</td>

<td class="gt_row gt_right">

410,901

</td>

<td class="gt_row gt_right">

188,028

</td>

<td class="gt_row gt_right">

30,954

</td>

<td class="gt_row gt_right">

21,111

</td>

<td class="gt_row gt_right">

24,680

</td>

<td class="gt_row gt_right">

175,735

</td>

<td class="gt_row gt_right">

103,329

</td>

<td class="gt_row gt_right">

146,413

</td>

<td class="gt_row gt_right">

72,777

</td>

<td class="gt_row gt_right">

34,698

</td>

<td class="gt_row gt_right">

104,754

</td>

<td class="gt_row gt_right">

51,888

</td>

<td class="gt_row gt_right">

139,005

</td>

<td class="gt_row gt_right">

139,823

</td>

</tr>

<tr>

<td class="gt_row gt_right">

320,055

</td>

<td class="gt_row gt_right">

237,188

</td>

<td class="gt_row gt_right">

1,738,334

</td>

<td class="gt_row gt_right">

1,346,724

</td>

<td class="gt_row gt_right">

96,678

</td>

<td class="gt_row gt_right">

700,615

</td>

<td class="gt_row gt_right">

136,435

</td>

<td class="gt_row gt_right">

191,077

</td>

<td class="gt_row gt_right">

724,243

</td>

<td class="gt_row gt_right">

989,638

</td>

<td class="gt_row gt_right">

72,067

</td>

<td class="gt_row gt_right">

461,658

</td>

<td class="gt_row gt_right">

489,023

</td>

<td class="gt_row gt_right">

276,600

</td>

<td class="gt_row gt_right">

410,270

</td>

<td class="gt_row gt_right">

192,067

</td>

<td class="gt_row gt_right">

29,723

</td>

<td class="gt_row gt_right">

21,430

</td>

<td class="gt_row gt_right">

26,393

</td>

<td class="gt_row gt_right">

176,136

</td>

<td class="gt_row gt_right">

102,999

</td>

<td class="gt_row gt_right">

151,116

</td>

<td class="gt_row gt_right">

70,462

</td>

<td class="gt_row gt_right">

35,177

</td>

<td class="gt_row gt_right">

114,175

</td>

<td class="gt_row gt_right">

51,820

</td>

<td class="gt_row gt_right">

138,376

</td>

<td class="gt_row gt_right">

176,415

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

### Dispatchable generation units

The file has the name `gen.csv` and contains a table with a row per each
dispatchable generating unit (i.e. no variable generation units like
wind and solar). Each row has the following fields:

  - `Unit`: unit name
  - `bus`: the index (from 0 to `N`) of the zone where the unit belongs.
    The zones are in the order specified in the demand files (and also
    non-dispatchable renewables)
  - `Technology` and `Fuel`: code of technology and fuel based on the
    [Dispa-SET
    classification](http://www.dispaset.eu/en/latest/data.html?#technologies)
  - `cost`: cost of electricity generation (EUR/MWh)
  - `co2_per_mwh`: CO2 emission per MWh
  - `max`: Maximum daily generation of the unit (MWh)
  - `stomax`: Maximum value of the storage (MWh)
  - `min`: Minimum daily generation of the unit (MWh)
  - `stomin`: Minimum value of the storage (MWh)

Here an example of the file `db/envarclim/1990/gen.csv`.

<!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#ewwbdrjkuz .gt_table {
  display: table;
  border-collapse: collapse;
  margin-left: auto;
  margin-right: auto;
  color: #333333;
  font-size: smaller;
  background-color: #FFFFFF;
  width: auto;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #A8A8A8;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #A8A8A8;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
}

#ewwbdrjkuz .gt_heading {
  background-color: #FFFFFF;
  text-align: center;
  border-bottom-color: #FFFFFF;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
}

#ewwbdrjkuz .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#ewwbdrjkuz .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#ewwbdrjkuz .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#ewwbdrjkuz .gt_col_headings {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
}

#ewwbdrjkuz .gt_col_heading {
  color: #333333;
  background-color: #FFFFFF;
  font-size: smaller;
  font-weight: bold;
  text-transform: inherit;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: bottom;
  padding-top: 5px;
  padding-bottom: 6px;
  padding-left: 5px;
  padding-right: 5px;
  overflow-x: hidden;
}

#ewwbdrjkuz .gt_column_spanner_outer {
  color: #333333;
  background-color: #FFFFFF;
  font-size: smaller;
  font-weight: bold;
  text-transform: inherit;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 4px;
  padding-right: 4px;
}

#ewwbdrjkuz .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#ewwbdrjkuz .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#ewwbdrjkuz .gt_column_spanner {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  vertical-align: bottom;
  padding-top: 5px;
  padding-bottom: 6px;
  overflow-x: hidden;
  display: inline-block;
  width: 100%;
}

#ewwbdrjkuz .gt_group_heading {
  padding: 8px;
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  text-transform: inherit;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: middle;
}

#ewwbdrjkuz .gt_empty_group_heading {
  padding: 0.5px;
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  vertical-align: middle;
}

#ewwbdrjkuz .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#ewwbdrjkuz .gt_from_md > :first-child {
  margin-top: 0;
}

#ewwbdrjkuz .gt_from_md > :last-child {
  margin-bottom: 0;
}

#ewwbdrjkuz .gt_row {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 5px;
  padding-right: 5px;
  margin: 10px;
  border-top-style: solid;
  border-top-width: 1px;
  border-top-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: middle;
  overflow-x: hidden;
}

#ewwbdrjkuz .gt_stub {
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  text-transform: inherit;
  border-right-style: solid;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
  padding-left: 12px;
}

#ewwbdrjkuz .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#ewwbdrjkuz .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#ewwbdrjkuz .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#ewwbdrjkuz .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#ewwbdrjkuz .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#ewwbdrjkuz .gt_footnotes {
  color: #333333;
  background-color: #FFFFFF;
  border-bottom-style: none;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
}

#ewwbdrjkuz .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#ewwbdrjkuz .gt_sourcenotes {
  color: #333333;
  background-color: #FFFFFF;
  border-bottom-style: none;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
}

#ewwbdrjkuz .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#ewwbdrjkuz .gt_left {
  text-align: left;
}

#ewwbdrjkuz .gt_center {
  text-align: center;
}

#ewwbdrjkuz .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#ewwbdrjkuz .gt_font_normal {
  font-weight: normal;
}

#ewwbdrjkuz .gt_font_bold {
  font-weight: bold;
}

#ewwbdrjkuz .gt_font_italic {
  font-style: italic;
}

#ewwbdrjkuz .gt_super {
  font-size: 65%;
}

#ewwbdrjkuz .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="ewwbdrjkuz" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="10" class="gt_heading gt_title gt_font_normal" style>

<strong>Generation
units</strong>

</th>

</tr>

<tr>

<th colspan="10" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First five
units

</th>

</tr>

</thead>

<thead class="gt_col_headings">

<tr>

<th class="gt_col_heading gt_columns_bottom_border gt_left" rowspan="1" colspan="1">

Unit

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

bus

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_left" rowspan="1" colspan="1">

Technology

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_left" rowspan="1" colspan="1">

Fuel

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

cost

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

co2\_per\_mwh

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

max

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

stomax

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

min

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

stomin

</th>

</tr>

</thead>

<tbody class="gt_table_body">

<tr>

<td class="gt_row gt_left">

NL\_Nuclear energy

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_left">

STUR

</td>

<td class="gt_row gt_left">

NUC

</td>

<td class="gt_row gt_right">

3.00

</td>

<td class="gt_row gt_right">

0.00

</td>

<td class="gt_row gt_right">

11664

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

9914.4

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_left">

NL\_Biomass fleet

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_left">

STUR

</td>

<td class="gt_row gt_left">

BIO

</td>

<td class="gt_row gt_right">

7.03

</td>

<td class="gt_row gt_right">

0.00

</td>

<td class="gt_row gt_right">

9552

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0.0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_left">

NL\_CCGT fleet E class

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_left">

COMC

</td>

<td class="gt_row gt_left">

GAS

</td>

<td class="gt_row gt_right">

67.56

</td>

<td class="gt_row gt_right">

0.39

</td>

<td class="gt_row gt_right">

5016

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0.0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_left">

NL\_CCGT fleet F class

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_left">

COMC

</td>

<td class="gt_row gt_left">

GAS

</td>

<td class="gt_row gt_right">

48.46

</td>

<td class="gt_row gt_right">

0.21

</td>

<td class="gt_row gt_right">

271920

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0.0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_left">

NL\_CCGT fleet G\_H class

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_left">

COMC

</td>

<td class="gt_row gt_left">

GAS

</td>

<td class="gt_row gt_right">

42.46

</td>

<td class="gt_row gt_right">

0.19

</td>

<td class="gt_row gt_right">

32592

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0.0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

### Transmission lines

The file has the name `lin.csv` and contains a table with a row per each
line. Lines represents the cross-border transmission lines connecting
two zones. Each line consists of the name of the line, the two connected
zones (used an integer index as in the `bus` field in the generation
units) and the maximum daily capacity (MWh).

Here an example.

<!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#tsoyqykgjh .gt_table {
  display: table;
  border-collapse: collapse;
  margin-left: auto;
  margin-right: auto;
  color: #333333;
  font-size: smaller;
  background-color: #FFFFFF;
  width: auto;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #A8A8A8;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #A8A8A8;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
}

#tsoyqykgjh .gt_heading {
  background-color: #FFFFFF;
  text-align: center;
  border-bottom-color: #FFFFFF;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
}

#tsoyqykgjh .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#tsoyqykgjh .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#tsoyqykgjh .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#tsoyqykgjh .gt_col_headings {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
}

#tsoyqykgjh .gt_col_heading {
  color: #333333;
  background-color: #FFFFFF;
  font-size: smaller;
  font-weight: bold;
  text-transform: inherit;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: bottom;
  padding-top: 5px;
  padding-bottom: 6px;
  padding-left: 5px;
  padding-right: 5px;
  overflow-x: hidden;
}

#tsoyqykgjh .gt_column_spanner_outer {
  color: #333333;
  background-color: #FFFFFF;
  font-size: smaller;
  font-weight: bold;
  text-transform: inherit;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 4px;
  padding-right: 4px;
}

#tsoyqykgjh .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#tsoyqykgjh .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#tsoyqykgjh .gt_column_spanner {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  vertical-align: bottom;
  padding-top: 5px;
  padding-bottom: 6px;
  overflow-x: hidden;
  display: inline-block;
  width: 100%;
}

#tsoyqykgjh .gt_group_heading {
  padding: 8px;
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  text-transform: inherit;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: middle;
}

#tsoyqykgjh .gt_empty_group_heading {
  padding: 0.5px;
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  vertical-align: middle;
}

#tsoyqykgjh .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#tsoyqykgjh .gt_from_md > :first-child {
  margin-top: 0;
}

#tsoyqykgjh .gt_from_md > :last-child {
  margin-bottom: 0;
}

#tsoyqykgjh .gt_row {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 5px;
  padding-right: 5px;
  margin: 10px;
  border-top-style: solid;
  border-top-width: 1px;
  border-top-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 1px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 1px;
  border-right-color: #D3D3D3;
  vertical-align: middle;
  overflow-x: hidden;
}

#tsoyqykgjh .gt_stub {
  color: #333333;
  background-color: #FFFFFF;
  font-size: 100%;
  font-weight: initial;
  text-transform: inherit;
  border-right-style: solid;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
  padding-left: 12px;
}

#tsoyqykgjh .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#tsoyqykgjh .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#tsoyqykgjh .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#tsoyqykgjh .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#tsoyqykgjh .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#tsoyqykgjh .gt_footnotes {
  color: #333333;
  background-color: #FFFFFF;
  border-bottom-style: none;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
}

#tsoyqykgjh .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#tsoyqykgjh .gt_sourcenotes {
  color: #333333;
  background-color: #FFFFFF;
  border-bottom-style: none;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
  border-left-style: none;
  border-left-width: 2px;
  border-left-color: #D3D3D3;
  border-right-style: none;
  border-right-width: 2px;
  border-right-color: #D3D3D3;
}

#tsoyqykgjh .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#tsoyqykgjh .gt_left {
  text-align: left;
}

#tsoyqykgjh .gt_center {
  text-align: center;
}

#tsoyqykgjh .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#tsoyqykgjh .gt_font_normal {
  font-weight: normal;
}

#tsoyqykgjh .gt_font_bold {
  font-weight: bold;
}

#tsoyqykgjh .gt_font_italic {
  font-style: italic;
}

#tsoyqykgjh .gt_super {
  font-size: 65%;
}

#tsoyqykgjh .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="tsoyqykgjh" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="4" class="gt_heading gt_title gt_font_normal" style>

<strong>Transmission
lines</strong>

</th>

</tr>

<tr>

<th colspan="4" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First five
lines

</th>

</tr>

</thead>

<thead class="gt_col_headings">

<tr>

<th class="gt_col_heading gt_columns_bottom_border gt_left" rowspan="1" colspan="1">

line\_name

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

from

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

to

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

cap

</th>

</tr>

</thead>

<tbody class="gt_table_body">

<tr>

<td class="gt_row gt_left">

AT-CH

</td>

<td class="gt_row gt_right">

7

</td>

<td class="gt_row gt_right">

15

</td>

<td class="gt_row gt_right">

28800

</td>

</tr>

<tr>

<td class="gt_row gt_left">

AT-CZ

</td>

<td class="gt_row gt_right">

7

</td>

<td class="gt_row gt_right">

19

</td>

<td class="gt_row gt_right">

21600

</td>

</tr>

<tr>

<td class="gt_row gt_left">

AT-DE

</td>

<td class="gt_row gt_right">

7

</td>

<td class="gt_row gt_right">

3

</td>

<td class="gt_row gt_right">

60600

</td>

</tr>

<tr>

<td class="gt_row gt_left">

AT-HU

</td>

<td class="gt_row gt_right">

7

</td>

<td class="gt_row gt_right">

20

</td>

<td class="gt_row gt_right">

19200

</td>

</tr>

<tr>

<td class="gt_row gt_left">

AT-IT

</td>

<td class="gt_row gt_right">

7

</td>

<td class="gt_row gt_right">

8

</td>

<td class="gt_row gt_right">

8160

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

### Ren

### Inflow

### Availability

## Outputs

## Available simulations
