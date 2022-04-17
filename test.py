"""
Created on Sat Apr 16 20:32:00 2022
@author: austi
"""
import csv
import phonenumbers
from phonenumbers import geocoder as gc
from opencage.geocoder import OpenCageGeocode

# Track Phone using Number

number = phonenumbers.parse('+15713830830')
key = '151375cccb7b4b48bd8cb3bb5b0c8ddd';
f = open('Data.csv', 'w')
writer = csv.writer(f)

count2=0

while count2<1:
    yourLocation = gc.description_for_number(number, 'en')
    
    geocoder = OpenCageGeocode(key)
    
    query = str(yourLocation)
    
    results = geocoder.geocode(query)
    count2+=1
    lat = results[0]['geometry']['lat']
    lng = results[0]['geometry']['lng']
    writer.writerow([lat,lng]) 
    quit() 
f.close()