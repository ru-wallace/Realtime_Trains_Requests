# NOTE: As of 2024-01-20 the API seems to be returning incorrect results.
### I'm trying to work out if it's a problem with requests generated in this code, but it seems to happen everywhere.


## Summary

A Python script to display rail and connected transportation services using the [Realtime Trains API](https://www.realtimetrains.co.uk/about/developer/pull/docs/) using a console based UI.

## Requirements

User must have a [Realtime Trains API account](https://api.rtt.io/) and include a .env environment file containing the following lines (fill in your own username and password):


    USER=[username]
    PASSWORD=[password]


Create a conda environment using the [environment.yml](environment.yml) file using the below command or install the relevant dependencies listed in the file through other means.

    conda env create -f environment.yml

## Guide

Find CRS code of stations matching search term:

    [search|s] [term]
        
Get arrivals for given station:
  
    [arrivals|a|arr|arrs] [crs code]
        
Get departures for given station:

    [departures|d|dep|deps] [crs code]
    
Get all services for given station:

    [all|ad|ads|arrdep|arrsdeps|a+d] [crs code]

View help information:

    [?|help]
    
Close program:

    [exit|quit|escape|x|q]


    


