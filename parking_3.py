from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import sched,time
import os
import threading
import socket
from twisted.internet import task, reactor

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-cbac1ba8-84b2-469d-a59b-7d66d9b4cb2a'
pnconfig.subscribe_key = 'sub-c-88b6488e-3adb-11eb-b6eb-96faa39b9528'
pnconfig.ssl = True
pubnub = PubNub(pnconfig)

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
        if(message.message == "Currently_Occupied"):
        	print("Parking Slot Status: OCCUPIED by Vehicle-3")
        	reactor.stop()
        else:
        	print("Parking Slot Status: ",message.message)
        
        
        
parking_lat = 53.3719403591678
parking_long = -6.253026535629358



parking_values = ["EMPTY"]#,"OCCUPIED"]

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels("parking-3").execute()

parking_time = 5.0 #5 seconds
#Runs every 5 seconds
def operate_signal():
	pubnub.publish().channel("parking-3").message(str(parking_values[0])).pn_async(my_publish_callback)
	time.sleep(10)
	#pubnub.publish().channel("parking-3").message(str(parking_values[1])).pn_async(my_publish_callback)
	#time.sleep(10)
	

l = task.LoopingCall(operate_signal)
l.start(parking_time)

reactor.run()











        
