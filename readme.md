# Weather Data Converter

Weather  Data  Converter  is  a  software  tool that  automatically  fetches  the  hourly  climate  data  for  a  given
location  provided  by  the  DWD  –  Deutscher  Wetterdienst  on  its  FTP  server, Then it converts it to a EPW
file format that is supported by programs for building physics analysis such  as  Therakles,  Delphin,  as  well  as
other  programs  that  use  the  EnergyPlus  core.

## Getting Started

### Prerequisites

* Python (program was written and tested in version 3.6.3)

Following libraries:
* PyQt5
* pvlib
* PrettyTable

### Instalation

To get the full functionality of the program, it's necessary to enter your own Google Maps API key in the source code.

To do this, open the 'gui/map.html' file and in the line number 13, change the string '<YOUR API HERE>' with your own API key.

