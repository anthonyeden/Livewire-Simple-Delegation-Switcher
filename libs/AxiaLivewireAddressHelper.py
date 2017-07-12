""" Helper methods for Axia Livewire Audio-Over-IP Multicast Addresses.
Inspired by https://gist.github.com/kylophone/a10e2c88ced3bf5e7674 """

import sys
import struct
import win_inet_pton
import socket


__author__ = "Anthony Eden"
__copyright__ = "Copyright 2015, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden", "Kyle Swanson"]
__license__ = "GPL"
__version__ = "1.0.0"

    
def streamNumToMulticastAddr(streamNum, format = "standard"):
    """ Takes a stream number and stream format, and returns the multicast address for the audio """
    
    startAddress = streamFormatBaseIp(format)
    startAddressDecimal = ipToDecimal(startAddress)
    
    return decimalToIp(int(streamNum) + startAddressDecimal)

def multicastAddrToStreamNum(multicastAddr):
    """ Takes a multicast address and returns the Livewire stream number """
    
    format = streamFormatFromMulticastAddr(multicastAddr)
    formatBaseIp = streamFormatBaseIp(format)
    formatBaseIpDecimal = ipToDecimal(formatBaseIp)
    
    multicastAddrDecimal = ipToDecimal(multicastAddr)
    
    return multicastAddrDecimal - formatBaseIpDecimal

def streamFormatBaseIp(format = "standard"):
    """ Takes a Livewire multicast format and returns the multicast base IP address """
    
    if format == "standard" or format == "livestream":
        startAddress = "239.192.0.0"
    
    elif format == "backfeed_standard":
        startAddress = "239.193.0.0"
    
    elif format == "backfeed_livestream":
        startAddress = "239.195.0.0"
    
    elif format == "surround":
        startAddress = "239.196.0.0"
    
    else:
        raise ValueError("Invalid format specified. Must be standard, livestream. backfeed_standard, backfeed_livestream, or surround.")
    
    return startAddress

def streamFormatFromMulticastAddr(ipAddress):
    """ Takes a Livewire multicast IP address and returns the Livewire format """
    
    addressSegments = ipAddress.split('.');
    formatSegment = int(addressSegments[1])
    
    if formatSegment == 192:
        # We can't be sure if this is a standard stream or livestream
        return "standard"
        
    elif formatSegment == 193:
        return "backfeed_standard"
        
    elif formatSegment == 195:
        return "backfeed_livestream"
        
    elif formatSegment == 196:
        return "backfeed_surround"
        
    else:
        raise ValueError("Unknown stream format")
    

def ipToDecimal(originalIp):
    """ Takes a standard dotted-quad IP Address and returns it as an integer """
    
    ipStruct = socket.inet_pton(socket.AF_INET, originalIp)
    (ipDecimal, ) = struct.unpack(">L", ipStruct)
    return ipDecimal

def decimalToIp(originalDecimal):
    """ Takes a integer-based IP Address and returns it as the standard dotted-quad format """
    
    ipStruct = struct.pack(">L", originalDecimal)
    return socket.inet_ntoa(ipStruct)

