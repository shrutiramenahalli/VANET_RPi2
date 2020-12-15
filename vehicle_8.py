from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import sched,time
import os
import threading
from geopy.distance import geodesic
import socket
from datetime import datetime, timedelta
import json

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-cbac1ba8-84b2-469d-a59b-7d66d9b4cb2a'
pnconfig.subscribe_key = 'sub-c-88b6488e-3adb-11eb-b6eb-96faa39b9528'
pnconfig.ssl = True
pubnub = PubNub(pnconfig)

accidentDataPostResponse = None

def storeAccidentData(message):
    accidentDataFetched = []
    if "body" in message:
        print("hola",message)
        output = message['body']
        print(output)
        for acccidentSignal in output:
            timestamp = acccidentSignal['timeStamp']
            date_time_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            if abs(datetime.now() - date_time_obj) < timedelta(minutes=200):
                accidentDataFetched.append(acccidentSignal)
            print("******")
        return accidentDataFetched
    else:
        return accidentDataFetched



def my_publish_callback(envelope, status):
   # Check whether request successfully completed or not
    if not status.is_error():
        pass
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass
    def status(self, pubnub, status):
        pass
    def message(self, pubnub, message):
        if message.message == None:
            continue_moving()
        else:
            print("From RSU-2 : ",message.message)
            continue_moving(message.message)


#RSU 2
RSU_coords = [53.373931, -6.243970]
vehicle_8_start_coords = [53.374973, -6.247235]
vehicle_8_stop_coords = [53.376226, -6.242144]
junction_coords = [53.373887, -6.243210]

def continue_moving(message):
    accidentDataFetched = storeAccidentData(message)
    print(accidentDataFetched)
    pubnub.unsubscribe().channels("RSU-2").execute()
    if(checkAccidentDistance(accidentDataFetched)):
        changeLanes(accidentDataFetched)
    else:
        while(vehicle_8_start_coords[0] >= vehicle_8_stop_coords[0] and vehicle_8_start_coords[1] <= vehicle_8_stop_coords[1]):
            vehicle_8_start_coords[0] = round((vehicle_8_start_coords[0] - 0.00001),6)
            vehicle_8_start_coords[1] = round((vehicle_8_start_coords[1] + 0.00001),6)
            print("Current Coordinates", vehicle_8_start_coords[0],vehicle_8_start_coords[1])
            time.sleep(1)

def checkAccidentDistance(accidentDataFetched):
    print("Checking if route change is needed on the basis of accident location !")
    accidentCount = len(accidentDataFetched)
    print(accidentCount, "accidents detected ! ")
    vehicle_lane_change_coords = []
    arrayCounter = 0
    for accidentLoc in accidentDataFetched:
        print("Accident detected at ", accidentLoc['accidentLongitude'] + ", " +accidentLoc['accidentLatitude'])
        vehicle_lane_change_coords.append([accidentLoc['accidentLongitude'], accidentLoc['accidentLatitude']])
        distanceToAccident = geodesic([vehicle_8_start_coords[0],vehicle_8_start_coords[1]],[accidentLoc['accidentLongitude'], accidentLoc['accidentLatitude']]).m        
        print("Distance to Accident Spot (metres): ",distanceToAccident)
        if distanceToAccident < 350:
            print("Need to change route !")
            return True
    print("No need to change routes !")
    return False

def changeLanes(accidentDataFetched):
    pubnub.unsubscribe().channels("RSU-2").execute()
    accidentCount = len(accidentDataFetched)
    print(accidentCount, "accidents detected ! ")
    vehicle_lane_change_coords = []
    arrayCounter = 0
    accident_coords = []
    for accidentLoc in accidentDataFetched:
        vehicle_lane_change_coords.append([accidentLoc['accidentLongitude'], accidentLoc['accidentLatitude']])
        accident_coords.append([accidentLoc['accidentLongitude'], accidentLoc['accidentLatitude']])
    print(vehicle_8_start_coords)
    print(vehicle_8_stop_coords)
    print("Junction loc - ", junction_coords)
    while((geodesic(vehicle_8_start_coords,junction_coords).m) > 10):
        print("Distance to Junction (metres): ",geodesic(vehicle_8_start_coords,junction_coords).m)
        vehicle_8_start_coords[0] = round((vehicle_8_start_coords[0] - 0.0000049),6)
        vehicle_8_start_coords[1] = round((vehicle_8_start_coords[1] + 0.0000464),6)
        print("Current Coordinates", vehicle_8_start_coords[0],vehicle_8_start_coords[1])
    print("Vehicle at junction..")
    print("Changing lanes to avoid traffic congestion..")
    while(vehicle_8_start_coords[0] <= vehicle_8_stop_coords[0] and vehicle_8_start_coords[1] <= vehicle_8_stop_coords[1]):
            vehicle_8_start_coords[0] = round((vehicle_8_start_coords[0] + 0.0005),6)
            vehicle_8_start_coords[1] = round((vehicle_8_start_coords[1] + 0.0005),6)
            print("Current Coordinates", vehicle_8_start_coords[0],vehicle_8_start_coords[1])
    print("Vehicle 8 reached destination !")


def moving_vehicle():
    while((geodesic(vehicle_8_start_coords,RSU_coords).m) > 15):
        print("Distance to RSU-2 (metres): ",geodesic(vehicle_8_start_coords,RSU_coords).m)
        time.sleep(0.5)
        vehicle_8_start_coords[0] = round((vehicle_8_start_coords[0] - 0.0000521),6)
        vehicle_8_start_coords[1] = round((vehicle_8_start_coords[1] + 0.00016325),6)
        print("Current Coordinates", vehicle_8_start_coords[0],vehicle_8_start_coords[1])
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels("RSU-2").execute()
moving_vehicle()