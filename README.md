## Summary

A Python script to display rail and connected transportation services using the [Realtime Trains API](https://www.realtimetrains.co.uk/about/developer/pull/docs/) using a console based UI

## Requirements

User must have a [Realtime Trains API account](https://api.rtt.io/) and include a .env environment file containing the following lines (fill in your own username and password):


    USER=[username]
    PASSWORD=[password]

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


    


