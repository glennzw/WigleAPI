# Wigle API

Small Python wrapper for Wigle's new API. Given an SSID, will lookup via Wigle and OpenStreetMap.

### Usage:
```
>>> import wigle_api
>>> w = Wigle()
>>> result = w.lookupSSID("Apple Network 88b445") #Returns a list of results
>>> print r[0]['longaddress']

FBI, 935, Pennsylvania Avenue Northwest, Penn Quarter, Washington, District of Columbia, 20535, United States of America
```

### Config
Create a config file in the same directory called wigle.conf. For example:
```
[wigle]
user: 13371337133713371337133713371337
key: 12345123451234512345123451234512
email: glenn@internet.com
maxresults: 20
```

The `user` and `key` values can be obtained from https://api.wigle.net/

### Notes
Will currently only lookup the first 100 results.
The maxresults parameter refers to the maximum number of returned results to do OpenStreetMaps lookup against. i.e if Wigle returns more than maxresults the street lookup won't be conducted (but the Wigle GPS data will still be returned, with the overflow value set to 1). 
