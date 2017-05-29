#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @glennzw
# Wigle API. Populate wigle.conf with your API keys / email. See https://api.wigle.net/
# Uses OpenStreetMap to lookup addresses, if number of Wigle results < maxresults
# ToDo: Collapse results that are close together using haversine (https://github.com/sensepost/Snoopy/blob/master/snoopy/server/bin/wigle_api_lite.py#L114)
import requests
import logging
import json
import ConfigParser
from requests.auth import HTTPBasicAuth

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.ERROR)

class Wigle(object):

    def __init__(self,confFile='wigle.conf'):
        Config = ConfigParser.ConfigParser()
        Config.read(confFile)
        try:
            user = Config.get('wigle','user')
            key = Config.get('wigle','key')
            self.email = Config.get('wigle','email')
        except:
            raise ValueError('Please enter your API key into the wigle.conf file. See https://api.wigle.net/')
        if user == "changeme" or key == "changeme" or self.email == "changeme":
            raise ValueError('Please enter your API key into the wigle.conf file. See https://api.wigle.net/')
        self.max_results = 20
        try:
            self.max_results = int(Config.get('wigle','maxresults'))
        except:
            pass
        self.auth = HTTPBasicAuth(user, key)

    def __getAddress(self,gps_lat,gps_long):
        """Get street address from GPS coordinates"""
        lookup_url = "http://nominatim.openstreetmap.org/reverse?zoom=18&addressdetails=1&format=json&email=%s&lat=%s&lon=%s" %(self.email,gps_lat,gps_long)
        try:
            req = requests.get(lookup_url)
            if req.status_code == 200 and 'json' in req.headers['content-type']:
                #addj = json.loads(req.text.encode('UTF8'))
                addj = json.loads(req.text.encode('utf-8'))
                longaddress = addj.get('display_name', '')
                compound_address = addj.get('address', {})
                city = compound_address.get('city', '')
                country = compound_address.get('country', '')
                country_code = compound_address.get('country_code', '')
                county = compound_address.get('county', '')
                postcode = compound_address.get('postcode', '')
                housenumber = compound_address.get('house_number', '')
                road = compound_address.get('road', '')
                state = compound_address.get('state', '')
                suburb = compound_address.get('suburb', '')
                shortaddress = "%s %s, %s" %(housenumber, road, city)
                shortaddress = shortaddress.strip()
            return {'longaddress':longaddress, 'shortaddress':shortaddress, 'city':city, 'country':country, 'code':country_code, 'county':county, 'postcode':postcode, 'road':road, 'state':state, 'suburb':suburb}
        except Exception,e:
            logging.error("Unable to retrieve address from OpenStreetMap - '%s'" % str(e))


    def lookupSSID(self,ssid):
      """Lookup an SSID via Wigle and OpenStreetMap"""
      r = requests.get("https://api.wigle.net/api/v2/network/search?first=0&freenet=false&paynet=false&ssid=%s" % ssid, auth=self.auth)
      if r.status_code != 200:
        logging.error("Unable to lookup %s, bad status: %d. Have you set your API keys correctly?" % (ssid, r.status_code))
        return
      try:
        result = r.json() #Depending on package version json is either a function or a value. FML.
      except:
          try:
              result = r.json #Depending on package version json is either a function or a value. FML.
          except Exception, e:
              logging.error("Unable to decode JSON response for %s" %ssid)
              logging.error(e)
              return

      overflow = 0
      if result.get('resultCount') > self.max_results:
          overflow = 1
      locations = result.get('results')
      locationsBuff = []
      for l in locations:
        tmpLocation = {"ssid":"", "lat":999, "long":999, "last_update":0, "mac":"000000000000", "overflow":-5, "longaddress":"", "shortaddress":"", "city":"", "code":"", "country":"", "county":"", "postcode":"", "road":"", "state":"", "suburb":""}
        upd = {'ssid':ssid,'mac':l['netid'], 'last_seen':l['lasttime'], 'last_update':l['lastupdt'], 'lat':float(l['trilat']), 'long':float(l['trilong']),'overflow':overflow}
        if not overflow:
            address = self.__getAddress(l['trilat'],l['trilong'])
            if address:
                tmpLocation.update(address)
        tmpLocation.update(upd)
        locationsBuff.append(tmpLocation)
      return locationsBuff

if __name__ == "__main__":
    import sys
    from pprint import pprint as pp
    if len(sys.argv) < 2:
        print "Supply SSID to lookup."
        exit(-1)
    w = Wigle()
    r = w.lookupSSID(sys.argv[1])
    pp(r)
