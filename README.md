  - [Yet Another Power System Model
    (YAPOS)](#yet-another-power-system-model-yapos)
      - [Installation](#installation)
      - [Getting started](#getting-started)
      - [Launching a simulation](#launch)
      - [Notes and caveats](#notes-and-caveats)
      - [How to set up and launch a simulation](#setup)
      - [Formulation](#formulation)
      - [Inputs](#inputs)
      - [Outputs](#outputs)
      - [Available simulations](#simulations)

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

## Launching a simulation

To launch a simulation you need to execute the script `main.py`
specifying two arguments: the path of the folder containing the input
files and the name of the simulation. This name will be used as name of
the NetCDF output.

## Notes and caveats

  - The model uses [Cbc solver](https://projects.coin-or.org/Cbc) as
    default solver, however the code might be easily adapted to use
    other solvers (e.g. GLPK)
  - The model interprets the input files in a “positional” fashion
    because our formulation converts the CSVs into information by
    position (using Pandas `iloc`). Then be careful when changing the
    inputs, all the dimensions (units, zones, etc.) MUST follow the same
    order in all the [input files](#inputs) and the name of the
    simulation that will be used to name the NetCDF output file.

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

Optimization variables

| Name                 | Description                                                     |
| :------------------- | :-------------------------------------------------------------- |
| `water_slack(g,t)`   | Slack for the storage balance constraint                        |
| `storage_slack(g,t)` | Slack for the constraint on the minimum storage                 |
| `curt_slack(n,t)`    | Slack for the constraint on the maximum curtailable electricity |

Slack variables

The optimization problem uses the following objective function:

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
electricity demand.

|     NL |     BE |      FR |      DE |    DK |     ES |     PT |     AT |     IT |      GB |    IE |     NO |     SE |     FI |     PL |     CH |    LT |    LV |    EE |     CZ |     HU |     RO |    SK |    SI |     BG |    HR |     RS |     GR |
| -----: | -----: | ------: | ------: | ----: | -----: | -----: | -----: | -----: | ------: | ----: | -----: | -----: | -----: | -----: | -----: | ----: | ----: | ----: | -----: | -----: | -----: | ----: | ----: | -----: | ----: | -----: | -----: |
| 292467 | 210703 | 1556073 | 1170710 | 92694 | 578629 | 111416 | 175029 | 632214 | 1019288 | 70998 | 473592 | 461015 | 254082 | 344699 | 170765 | 27211 | 19103 | 23523 | 163429 |  96521 | 144119 | 66929 | 31191 |  88687 | 40617 | 156689 | 117336 |
| 328015 | 244574 | 1720765 | 1392108 | 96407 | 706866 | 136122 | 201807 | 762106 |  985103 | 73619 | 468065 | 489230 | 279589 | 410901 | 188028 | 30954 | 21111 | 24680 | 175735 | 103329 | 146413 | 72777 | 34698 | 104754 | 51888 | 139005 | 139823 |
| 320055 | 237188 | 1738334 | 1346724 | 96678 | 700615 | 136435 | 191077 | 724243 |  989638 | 72067 | 461658 | 489023 | 276600 | 410270 | 192067 | 29723 | 21430 | 26393 | 176136 | 102999 | 151116 | 70462 | 35177 | 114175 | 51820 | 138376 | 176415 |

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

#gcwoldmmse .gt_table {
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

#gcwoldmmse .gt_heading {
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

#gcwoldmmse .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#gcwoldmmse .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#gcwoldmmse .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#gcwoldmmse .gt_col_headings {
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

#gcwoldmmse .gt_col_heading {
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

#gcwoldmmse .gt_column_spanner_outer {
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

#gcwoldmmse .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#gcwoldmmse .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#gcwoldmmse .gt_column_spanner {
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

#gcwoldmmse .gt_group_heading {
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

#gcwoldmmse .gt_empty_group_heading {
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

#gcwoldmmse .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#gcwoldmmse .gt_from_md > :first-child {
  margin-top: 0;
}

#gcwoldmmse .gt_from_md > :last-child {
  margin-bottom: 0;
}

#gcwoldmmse .gt_row {
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

#gcwoldmmse .gt_stub {
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

#gcwoldmmse .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#gcwoldmmse .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#gcwoldmmse .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#gcwoldmmse .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#gcwoldmmse .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#gcwoldmmse .gt_footnotes {
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

#gcwoldmmse .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#gcwoldmmse .gt_sourcenotes {
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

#gcwoldmmse .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#gcwoldmmse .gt_left {
  text-align: left;
}

#gcwoldmmse .gt_center {
  text-align: center;
}

#gcwoldmmse .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#gcwoldmmse .gt_font_normal {
  font-weight: normal;
}

#gcwoldmmse .gt_font_bold {
  font-weight: bold;
}

#gcwoldmmse .gt_font_italic {
  font-style: italic;
}

#gcwoldmmse .gt_super {
  font-size: 65%;
}

#gcwoldmmse .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="gcwoldmmse" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="10" class="gt_heading gt_title gt_font_normal" style>

<strong>Generation units</strong>

</th>

</tr>

<tr>

<th colspan="10" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First five units

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

#aiubsmndte .gt_table {
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

#aiubsmndte .gt_heading {
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

#aiubsmndte .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#aiubsmndte .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#aiubsmndte .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#aiubsmndte .gt_col_headings {
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

#aiubsmndte .gt_col_heading {
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

#aiubsmndte .gt_column_spanner_outer {
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

#aiubsmndte .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#aiubsmndte .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#aiubsmndte .gt_column_spanner {
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

#aiubsmndte .gt_group_heading {
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

#aiubsmndte .gt_empty_group_heading {
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

#aiubsmndte .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#aiubsmndte .gt_from_md > :first-child {
  margin-top: 0;
}

#aiubsmndte .gt_from_md > :last-child {
  margin-bottom: 0;
}

#aiubsmndte .gt_row {
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

#aiubsmndte .gt_stub {
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

#aiubsmndte .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#aiubsmndte .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#aiubsmndte .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#aiubsmndte .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#aiubsmndte .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#aiubsmndte .gt_footnotes {
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

#aiubsmndte .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#aiubsmndte .gt_sourcenotes {
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

#aiubsmndte .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#aiubsmndte .gt_left {
  text-align: left;
}

#aiubsmndte .gt_center {
  text-align: center;
}

#aiubsmndte .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#aiubsmndte .gt_font_normal {
  font-weight: normal;
}

#aiubsmndte .gt_font_bold {
  font-weight: bold;
}

#aiubsmndte .gt_font_italic {
  font-style: italic;
}

#aiubsmndte .gt_super {
  font-size: 65%;
}

#aiubsmndte .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="aiubsmndte" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="4" class="gt_heading gt_title gt_font_normal" style>

<strong>Transmission lines</strong>

</th>

</tr>

<tr>

<th colspan="4" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First five lines

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

### Non-dispatchable renewables

File name is `ren.csv` and contains a time-series per zone of the
generation from non-dispatchable renewables. The amount of electricity
specified will be generated unless curtailed.  
<!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#ilvhpsaoqq .gt_table {
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

#ilvhpsaoqq .gt_heading {
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

#ilvhpsaoqq .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#ilvhpsaoqq .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#ilvhpsaoqq .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#ilvhpsaoqq .gt_col_headings {
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

#ilvhpsaoqq .gt_col_heading {
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

#ilvhpsaoqq .gt_column_spanner_outer {
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

#ilvhpsaoqq .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#ilvhpsaoqq .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#ilvhpsaoqq .gt_column_spanner {
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

#ilvhpsaoqq .gt_group_heading {
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

#ilvhpsaoqq .gt_empty_group_heading {
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

#ilvhpsaoqq .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#ilvhpsaoqq .gt_from_md > :first-child {
  margin-top: 0;
}

#ilvhpsaoqq .gt_from_md > :last-child {
  margin-bottom: 0;
}

#ilvhpsaoqq .gt_row {
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

#ilvhpsaoqq .gt_stub {
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

#ilvhpsaoqq .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#ilvhpsaoqq .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#ilvhpsaoqq .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#ilvhpsaoqq .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#ilvhpsaoqq .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#ilvhpsaoqq .gt_footnotes {
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

#ilvhpsaoqq .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#ilvhpsaoqq .gt_sourcenotes {
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

#ilvhpsaoqq .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#ilvhpsaoqq .gt_left {
  text-align: left;
}

#ilvhpsaoqq .gt_center {
  text-align: center;
}

#ilvhpsaoqq .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#ilvhpsaoqq .gt_font_normal {
  font-weight: normal;
}

#ilvhpsaoqq .gt_font_bold {
  font-weight: bold;
}

#ilvhpsaoqq .gt_font_italic {
  font-style: italic;
}

#ilvhpsaoqq .gt_super {
  font-size: 65%;
}

#ilvhpsaoqq .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="ilvhpsaoqq" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="28" class="gt_heading gt_title gt_font_normal" style>

<strong>Daily renewable generation</strong>

</th>

</tr>

<tr>

<th colspan="28" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First three days

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

365

</td>

<td class="gt_row gt_right">

809

</td>

<td class="gt_row gt_right">

56,826

</td>

<td class="gt_row gt_right">

35,074

</td>

<td class="gt_row gt_right">

1,628

</td>

<td class="gt_row gt_right">

65,255

</td>

<td class="gt_row gt_right">

19,048

</td>

<td class="gt_row gt_right">

50,670

</td>

<td class="gt_row gt_right">

95,950

</td>

<td class="gt_row gt_right">

81,039

</td>

<td class="gt_row gt_right">

17,370

</td>

<td class="gt_row gt_right">

2,856

</td>

<td class="gt_row gt_right">

2,237

</td>

<td class="gt_row gt_right">

21,637

</td>

<td class="gt_row gt_right">

3,508

</td>

<td class="gt_row gt_right">

16,527

</td>

<td class="gt_row gt_right">

86

</td>

<td class="gt_row gt_right">

5

</td>

<td class="gt_row gt_right">

512

</td>

<td class="gt_row gt_right">

530

</td>

<td class="gt_row gt_right">

242

</td>

<td class="gt_row gt_right">

15,209

</td>

<td class="gt_row gt_right">

5

</td>

<td class="gt_row gt_right">

6,807

</td>

<td class="gt_row gt_right">

7,336

</td>

<td class="gt_row gt_right">

3,584

</td>

<td class="gt_row gt_right">

15,790

</td>

<td class="gt_row gt_right">

14,540

</td>

</tr>

<tr>

<td class="gt_row gt_right">

1,113

</td>

<td class="gt_row gt_right">

2,223

</td>

<td class="gt_row gt_right">

75,758

</td>

<td class="gt_row gt_right">

41,793

</td>

<td class="gt_row gt_right">

3,647

</td>

<td class="gt_row gt_right">

189,418

</td>

<td class="gt_row gt_right">

69,115

</td>

<td class="gt_row gt_right">

39,985

</td>

<td class="gt_row gt_right">

78,987

</td>

<td class="gt_row gt_right">

83,679

</td>

<td class="gt_row gt_right">

29,914

</td>

<td class="gt_row gt_right">

2,159

</td>

<td class="gt_row gt_right">

2,172

</td>

<td class="gt_row gt_right">

19,191

</td>

<td class="gt_row gt_right">

4,723

</td>

<td class="gt_row gt_right">

16,112

</td>

<td class="gt_row gt_right">

184

</td>

<td class="gt_row gt_right">

13

</td>

<td class="gt_row gt_right">

229

</td>

<td class="gt_row gt_right">

16

</td>

<td class="gt_row gt_right">

5

</td>

<td class="gt_row gt_right">

12,368

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

6,799

</td>

<td class="gt_row gt_right">

7,077

</td>

<td class="gt_row gt_right">

5,044

</td>

<td class="gt_row gt_right">

15,712

</td>

<td class="gt_row gt_right">

10,972

</td>

</tr>

<tr>

<td class="gt_row gt_right">

20,558

</td>

<td class="gt_row gt_right">

13,255

</td>

<td class="gt_row gt_right">

121,753

</td>

<td class="gt_row gt_right">

156,951

</td>

<td class="gt_row gt_right">

18,819

</td>

<td class="gt_row gt_right">

173,162

</td>

<td class="gt_row gt_right">

35,485

</td>

<td class="gt_row gt_right">

38,936

</td>

<td class="gt_row gt_right">

80,577

</td>

<td class="gt_row gt_right">

92,317

</td>

<td class="gt_row gt_right">

6,672

</td>

<td class="gt_row gt_right">

4,868

</td>

<td class="gt_row gt_right">

3,931

</td>

<td class="gt_row gt_right">

20,510

</td>

<td class="gt_row gt_right">

2,121

</td>

<td class="gt_row gt_right">

15,844

</td>

<td class="gt_row gt_right">

235

</td>

<td class="gt_row gt_right">

23

</td>

<td class="gt_row gt_right">

420

</td>

<td class="gt_row gt_right">

282

</td>

<td class="gt_row gt_right">

88

</td>

<td class="gt_row gt_right">

17,842

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

6,803

</td>

<td class="gt_row gt_right">

8,005

</td>

<td class="gt_row gt_right">

9,513

</td>

<td class="gt_row gt_right">

15,434

</td>

<td class="gt_row gt_right">

17,284

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

### Inflow

File name is `inflow.csv` and contains a time-series per unit of the
available energy available (MWh) for hydropower generation each day. The
file contains a column for **all** the units, then non-hydro units will
have a constant zero value.

<!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#hbfyodrhci .gt_table {
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

#hbfyodrhci .gt_heading {
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

#hbfyodrhci .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#hbfyodrhci .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#hbfyodrhci .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#hbfyodrhci .gt_col_headings {
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

#hbfyodrhci .gt_col_heading {
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

#hbfyodrhci .gt_column_spanner_outer {
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

#hbfyodrhci .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#hbfyodrhci .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#hbfyodrhci .gt_column_spanner {
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

#hbfyodrhci .gt_group_heading {
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

#hbfyodrhci .gt_empty_group_heading {
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

#hbfyodrhci .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#hbfyodrhci .gt_from_md > :first-child {
  margin-top: 0;
}

#hbfyodrhci .gt_from_md > :last-child {
  margin-bottom: 0;
}

#hbfyodrhci .gt_row {
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

#hbfyodrhci .gt_stub {
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

#hbfyodrhci .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#hbfyodrhci .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#hbfyodrhci .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#hbfyodrhci .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#hbfyodrhci .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#hbfyodrhci .gt_footnotes {
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

#hbfyodrhci .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#hbfyodrhci .gt_sourcenotes {
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

#hbfyodrhci .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#hbfyodrhci .gt_left {
  text-align: left;
}

#hbfyodrhci .gt_center {
  text-align: center;
}

#hbfyodrhci .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#hbfyodrhci .gt_font_normal {
  font-weight: normal;
}

#hbfyodrhci .gt_font_bold {
  font-weight: bold;
}

#hbfyodrhci .gt_font_italic {
  font-style: italic;
}

#hbfyodrhci .gt_super {
  font-size: 65%;
}

#hbfyodrhci .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="hbfyodrhci" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="205" class="gt_heading gt_title gt_font_normal" style>

<strong>Daily hydropower inflow</strong>

</th>

</tr>

<tr>

<th colspan="205" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First three days

</th>

</tr>

</thead>

<thead class="gt_col_headings">

<tr>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Oil fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet IGCC

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet IGCC

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Oil fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet G\_H class

</th>

</tr>

</thead>

<tbody class="gt_table_body">

<tr>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

67,770

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

36,439

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

19,169

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

52,165

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

71,357

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

83,616

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

67,168

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

8,894

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

29,888

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

8,110

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

6,998

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

6,154

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

4,877

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

12,388

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

69,383

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

64,742

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

26,159

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

51,637

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

69,157

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

81,907

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

62,475

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

8,659

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

28,928

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

8,143

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

7,007

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

5,897

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

4,853

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

12,753

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

69,561

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

73,321

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

30,802

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

48,501

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

68,115

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

81,879

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

59,912

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

8,415

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

28,331

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

8,338

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

7,044

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

5,869

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

4,767

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

12,782

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

### Availability

File `avail.csv` contains a time-series per zone of the availability
factor, a value between 1 (100% available generation) and 0 (unit non
available) for each unit.

<!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#ibsryfxjly .gt_table {
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

#ibsryfxjly .gt_heading {
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

#ibsryfxjly .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#ibsryfxjly .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#ibsryfxjly .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#ibsryfxjly .gt_col_headings {
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

#ibsryfxjly .gt_col_heading {
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

#ibsryfxjly .gt_column_spanner_outer {
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

#ibsryfxjly .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#ibsryfxjly .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#ibsryfxjly .gt_column_spanner {
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

#ibsryfxjly .gt_group_heading {
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

#ibsryfxjly .gt_empty_group_heading {
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

#ibsryfxjly .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#ibsryfxjly .gt_from_md > :first-child {
  margin-top: 0;
}

#ibsryfxjly .gt_from_md > :last-child {
  margin-bottom: 0;
}

#ibsryfxjly .gt_row {
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

#ibsryfxjly .gt_stub {
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

#ibsryfxjly .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#ibsryfxjly .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#ibsryfxjly .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#ibsryfxjly .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#ibsryfxjly .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#ibsryfxjly .gt_footnotes {
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

#ibsryfxjly .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#ibsryfxjly .gt_sourcenotes {
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

#ibsryfxjly .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#ibsryfxjly .gt_left {
  text-align: left;
}

#ibsryfxjly .gt_center {
  text-align: center;
}

#ibsryfxjly .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#ibsryfxjly .gt_font_normal {
  font-weight: normal;
}

#ibsryfxjly .gt_font_bold {
  font-weight: bold;
}

#ibsryfxjly .gt_font_italic {
  font-style: italic;
}

#ibsryfxjly .gt_super {
  font-size: 65%;
}

#ibsryfxjly .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="ibsryfxjly" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="205" class="gt_heading gt_title gt_font_normal" style>

<strong>Daily hydropower inflow</strong>

</th>

</tr>

<tr>

<th colspan="205" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First three days

</th>

</tr>

</thead>

<thead class="gt_col_headings">

<tr>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Oil fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet IGCC

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet IGCC

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Oil fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet G\_H class

</th>

</tr>

</thead>

<tbody class="gt_table_body">

<tr>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

</tr>

<tr>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

</tr>

<tr>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

<td class="gt_row gt_right">

1

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

### Minimum level of the storage

This file, named `stomin.csv`, contains a time-series per unit of the
minimum level of the storage. The value will be between `stomin` and
`stomax` specified in the [list of generation units](#gen). As for the
[inflow](#inflow) the table has a column for each unit, with a constant
zero for all the units without storage.

<!--html_preserve-->

<style>html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
}

#kbclybekfq .gt_table {
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

#kbclybekfq .gt_heading {
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

#kbclybekfq .gt_title {
  color: #333333;
  font-size: 125%;
  font-weight: initial;
  padding-top: 4px;
  padding-bottom: 4px;
  border-bottom-color: #FFFFFF;
  border-bottom-width: 0;
}

#kbclybekfq .gt_subtitle {
  color: #333333;
  font-size: 85%;
  font-weight: initial;
  padding-top: 0;
  padding-bottom: 4px;
  border-top-color: #FFFFFF;
  border-top-width: 0;
}

#kbclybekfq .gt_bottom_border {
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#kbclybekfq .gt_col_headings {
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

#kbclybekfq .gt_col_heading {
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

#kbclybekfq .gt_column_spanner_outer {
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

#kbclybekfq .gt_column_spanner_outer:first-child {
  padding-left: 0;
}

#kbclybekfq .gt_column_spanner_outer:last-child {
  padding-right: 0;
}

#kbclybekfq .gt_column_spanner {
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

#kbclybekfq .gt_group_heading {
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

#kbclybekfq .gt_empty_group_heading {
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

#kbclybekfq .gt_striped {
  background-color: rgba(128, 128, 128, 0.05);
}

#kbclybekfq .gt_from_md > :first-child {
  margin-top: 0;
}

#kbclybekfq .gt_from_md > :last-child {
  margin-bottom: 0;
}

#kbclybekfq .gt_row {
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

#kbclybekfq .gt_stub {
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

#kbclybekfq .gt_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#kbclybekfq .gt_first_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
}

#kbclybekfq .gt_grand_summary_row {
  color: #333333;
  background-color: #FFFFFF;
  text-transform: inherit;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
}

#kbclybekfq .gt_first_grand_summary_row {
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 5px;
  padding-right: 5px;
  border-top-style: double;
  border-top-width: 6px;
  border-top-color: #D3D3D3;
}

#kbclybekfq .gt_table_body {
  border-top-style: solid;
  border-top-width: 2px;
  border-top-color: #D3D3D3;
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-bottom-color: #D3D3D3;
}

#kbclybekfq .gt_footnotes {
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

#kbclybekfq .gt_footnote {
  margin: 0px;
  font-size: 90%;
  padding: 4px;
}

#kbclybekfq .gt_sourcenotes {
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

#kbclybekfq .gt_sourcenote {
  font-size: 90%;
  padding: 4px;
}

#kbclybekfq .gt_left {
  text-align: left;
}

#kbclybekfq .gt_center {
  text-align: center;
}

#kbclybekfq .gt_right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

#kbclybekfq .gt_font_normal {
  font-weight: normal;
}

#kbclybekfq .gt_font_bold {
  font-weight: bold;
}

#kbclybekfq .gt_font_italic {
  font-style: italic;
}

#kbclybekfq .gt_super {
  font-size: 65%;
}

#kbclybekfq .gt_footnote_marks {
  font-style: italic;
  font-size: 65%;
}
</style>

<div id="kbclybekfq" style="overflow-x:auto;overflow-y:auto;width:auto;height:auto;">

<table class="gt_table">

<thead class="gt_header">

<tr>

<th colspan="205" class="gt_heading gt_title gt_font_normal" style>

<strong>Daily hydropower inflow</strong>

</th>

</tr>

<tr>

<th colspan="205" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border" style>

First three days

</th>

</tr>

</thead>

<thead class="gt_col_headings">

<tr>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NL\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FR\_Oil fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet IGCC

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

DK\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

ES\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

AT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet IGCC

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IT\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GB\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

IE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

NO\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SE\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

FI\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Coal fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

PL\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CH\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LT\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

LV\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

EE\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

CZ\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_OCGT fleet Modern

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HU\_Oil fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet G\_H class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RO\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SK\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

SI\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Nuclear energy

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

BG\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet E class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Coal fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

HR\_Oil fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Hydro-reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_CCGT fleet cogen

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

RS\_Oil fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Hydro reservoir

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Biomass fleet

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_OCGT fleet Standard

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Lignite fleet Subcritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_Lignite fleet Supercritical

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet CHP

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet F class

</th>

<th class="gt_col_heading gt_columns_bottom_border gt_right" rowspan="1" colspan="1">

GR\_CCGT fleet G\_H class

</th>

</tr>

</thead>

<tbody class="gt_table_body">

<tr>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,012,019

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

2,525,081

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

645,450

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,877,565

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,422,859

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

18,440,832

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

9,210,462

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

763,170

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

4,066,876

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

323,852

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

119,237

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

104,881

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

14,848

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

489,718

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,012,019

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

2,525,081

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

645,450

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,877,565

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,422,859

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

18,440,832

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

9,210,462

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

763,170

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

4,066,876

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

323,852

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

119,237

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

104,881

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

14,848

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

489,718

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

<tr>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,012,019

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

2,525,081

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

645,450

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,877,565

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

1,422,859

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

18,440,832

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

9,210,462

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

763,170

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

4,066,876

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

323,852

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

119,237

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

104,881

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

14,848

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

489,718

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

<td class="gt_row gt_right">

0

</td>

</tr>

</tbody>

</table>

</div>

<!--/html_preserve-->

## Outputs

At the end of a YAPOS simulation, in the same folder of the input file
the model will save a set of files containing the results for the
simulation.

The main output file is in NetCDF format and the filename is set with
the keyword specified [when executing the simulation](#launch). In
addition to the NetCDF file, the simulation saves also a set of CSV
files in addition to a file named `model.lp`, containing the linear
programming formulation (that can be used for example to rerun the same
problem with another solver, e.g. GLPK).

### NetCDF output

``` python
import xarray as xr
xr.open_dataset('/Users/matteodefelice/work/yaposer/inst/extdata/es-pt-fr.nc')
```

    ## <xarray.Dataset>
    ## Dimensions:            (day: 365, line: 2, unit: 26, zone: 3)
    ## Coordinates:
    ##   * day                (day) int64 0 1 2 3 4 5 6 ... 358 359 360 361 362 363 364
    ##   * unit               (unit) object 'FR_Hydro reservoir' ... 'PT_Coal fleet Supercritical'
    ##   * zone               (zone) object 'ES' 'PT' 'FR'
    ##   * line               (line) object 'ES-FR' 'ES-PT'
    ## Data variables:
    ##     production         (day, unit) float64 ...
    ##     availability       (day, unit) float64 ...
    ##     inflow             (day, unit) float64 ...
    ##     storage_min        (day, unit) float64 ...
    ##     demand             (day, zone) int64 ...
    ##     renewables         (day, zone) float64 ...
    ##     flow               (day, line) float64 ...
    ##     shed_load          (day, zone) float64 ...
    ##     curtailed          (day, zone) float64 ...
    ##     storage_level      (day, unit) float64 ...
    ##     water_slack        (day, unit) float64 ...
    ##     storage_slack      (day, unit) float64 ...
    ##     curtailment_slack  (day, zone) float64 ...
    ##     unit_bus           (unit) int64 ...
    ##     unit_Technology    (unit) object ...
    ##     unit_Fuel          (unit) object ...
    ##     unit_cost          (unit) float64 ...
    ##     unit_co2_per_mwh   (unit) float64 ...
    ##     unit_max           (unit) float64 ...
    ##     unit_stomax        (unit) int64 ...
    ##     unit_min           (unit) float64 ...
    ##     unit_stomin        (unit) int64 ...
    ##     line_from          (line) int64 ...
    ##     line_to            (line) int64 ...
    ##     line_cap           (line) int64 ...
    ## Attributes:
    ##     created:          20/05/2020 21:44:19
    ##     hostname:         New-MacBook-Pro-2.local
    ##     model_folder:     db/test/
    ##     simulation_name:  test_run

## Available simulations
