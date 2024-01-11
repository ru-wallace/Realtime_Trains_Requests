## Summary

A Python script to display rail and connected transportation services using the [Realtime Trains API](https://www.realtimetrains.co.uk/about/developer/pull/docs/) using a console based UI

## Requirements

User must have a [Realtime Trains API account](https://api.rtt.io/) and include a .env environment file containing the following lines (fill in your own username and password):


    USER=[username]
    PASSWOORD=[password]

## Guide

    [search|s] [term]
        
Find CRS code of stations matching search term.
  
    [arrivals|a|arr|arrs] [crs code]
        
Get arrivals for given station.

    [departures|d|dep|deps] [crs code]
    
Get departures for given station.

    [all|ad|ads|arrdep|arrsdeps|a+d] [crs code]
    
Get all services for given station

    [exit|quit|escape|x|q]

Close program.

    [?|help]
    
View help information

