# HandleBinary: a class to handle binary files from LeCroy oscilloscopes

from os import remove
import numpy as np
import struct
import math
from datetime import datetime

from lib import Constants

# Note: buffer[i] is int, buffer[i:j] is bytes, where buffer is bytes
class HandleBinary:
    # instance variables
    # filePath: file path
    # readSuccess: whether read is succeeded (True) or not (False)
    # template: template name
    # commType: byte (1 byte) -> 0, word (2 bytes) -> 1
    # commOrder: big endian (high-order first) -> 0, little endian (low-order first) -> 1  
    #  f_f: format for float
    #  f_d: format for double
    #  f_w: format for short int (word)
    #  f_l: format for long int
    #  f_v: format for data value (byte or word)
    # length_WD: WAVEDESC length
    # length_UT: USERTEXT length
    # length_TT: TRIGTIME length
    # length_RT: RIS_TIME length
    # length_WA1: WAVE_ARRAY_1 length
    # length_WA2: WAVE_ARRAY_2 length
    # instName: instrument name
    # instNum: instrument number
    # traceLabel: waveform index
    # numData: number of data points
    # vGain: vertical gain
    # vOffset: vertical offset
    # vMax: max value
    # vMin: min value
    # hInterval: horizontal interval
    # hOffset: horizontal offset of the first point from the trigger
    # vUnit: vertical unit label
    # hUnit: horizontal unit label
    # time: triggered datetime
    # timeBase: integer representing the time per division
    # vCoupling: vertical coupling
    # vGain_f: fixed vertical gain
    # source: wave source
    # data: data
    def __init__(self, filePath):
        self.filePath=filePath
        self.readSuccess=True

        print(("Open {0:s}").format(self.filePath))
        with open(self.filePath, "rb") as f:
            buffer=b""
            # "#n"
            buffer=f.read(2)
            if buffer[0:1]!=b"#":
                print("Error: the 1st letter is not #")
                self.readSuccess=False
                return
            fileLenValue=int(buffer[1:2])
            buffer=f.read(fileLenValue)
            fileLen=int(buffer)
            print(("Total data size: {0:d}").format(fileLen))

            # WAVEDESC block
            ## descriptor name
            buffer=f.read(16)
            if buffer[0:8]!=b"WAVEDESC":
                print(("Error: {0:s} shold be \"WAVEDESC\"").format(buffer.decode()))
                self.readSuccess=False
                return

            ## template name
            buffer=f.read(16)
            self.template=removeNull(buffer)
            print(("Template: {0:s}").format(self.template))

            ## commType
            buffer=f.read(2)
            self.commType=buffer[0]
            if not self.commType in [0, 1]:
                print(("Error: commType {0:d} should be 0 or 1").format(self.commType))
                self.readSuccess=False
                return
            print(("commType: {0:d}").format(self.commType))

            ## commOrder
            buffer=f.read(2)
            self.commOrder=buffer[0]
            if not self.commOrder in [0, 1]:
                print(("Error: commOrder {0:d} should be 0 or 1").format(self.commOrder))
                self.readSuccess=False
                return
            print(("commOrder: {0:d}").format(self.commOrder))
            if self.commOrder==0:
                # big endian
                self.f_f=">f"
                self.f_d=">d"
                self.f_w=">h"
                self.f_l=">l"
                if self.commType==0:
                    # byte
                    self.f_v=">b"
                else:
                    # word
                    self.f_v=">h"
            else:
                # little endian
                self.f_f="<f"
                self.f_d="<d"
                self.f_w="<h"
                self.f_l="<l"
                if self.commType==0:
                    # byte
                    self.f_v="<b"
                else:
                    # word
                    self.f_v="<h"

            ## WAVEDESC length: should be 346
            buffer=f.read(4)
            self.length_WD=struct.unpack(self.f_l, buffer)[0]
            if self.length_WD!=346:
                print(("Error: WAVEDESC length {0:d} should be 346").format(self.length_WD))
                self.readSuccess=False
                return
            print(("WAVEDESC length: {0:d}").format(self.length_WD))

            ## USERTEXT length
            buffer=f.read(4)
            self.length_UT=struct.unpack(self.f_l, buffer)[0]
            print(("USERTEXT length: {0:d}").format(self.length_UT))

            ## ?
            buffer=f.read(4)

            ## TRIGTIME length
            buffer=f.read(4)
            self.length_TT=struct.unpack(self.f_l, buffer)[0]
            print(("TRIGTIME length: {0:d}").format(self.length_TT))

            ## RIS_TIME length
            buffer=f.read(4)
            self.length_RT=struct.unpack(self.f_l, buffer)[0]
            print(("RIS_TIME length: {0:d}").format(self.length_RT))

            ## reserved
            buffer=f.read(4)

            ## WAVE_ARRAY_1 length
            buffer=f.read(4)
            self.length_WA1=struct.unpack(self.f_l, buffer)[0]
            print(("WAVE_ARRAY_1 length: {0:d}").format(self.length_WA1))

            ## WAVE_ARRAY_2 length
            buffer=f.read(4)
            self.length_WA2=struct.unpack(self.f_l, buffer)[0]
            print(("WAVE_ARRAY_2 length: {0:d}").format(self.length_WA2))

            ## reserved
            buffer=f.read(8)

            ## instrument name
            buffer=f.read(16)
            self.instName=removeNull(buffer)
            print(("Instrument name: {0:s}").format(self.instName))

            ## instrument number
            buffer=f.read(4)
            self.instNum=struct.unpack(self.f_l, buffer)[0]
            print(("Instrument number: {0:d}").format(self.instNum))

            ## trace label
            buffer=f.read(16)
            self.traceLabel=removeNull(buffer)
            print(("Trace lebel: {0:s}").format(self.traceLabel))

            ## reserved
            buffer=f.read(4)

            ## number of data points
            buffer=f.read(4)
            self.numData=struct.unpack(self.f_l, buffer)[0]
            print(("Number of data: {0:d}").format(self.numData))

            ## unnecessary properties
            buffer=f.read(36)

            ## vertical gain
            buffer=f.read(4)
            self.vGain=struct.unpack(self.f_f, buffer)[0]
            print(("Vertical gain: {0:e}").format(self.vGain))

            ## vertical offset
            buffer=f.read(4)
            self.vOffset=struct.unpack(self.f_f, buffer)[0]
            print(("Vertical offset: {0:e}").format(self.vOffset))

            ## max value
            buffer=f.read(4)
            self.vMax=struct.unpack(self.f_f, buffer)[0]
            print(("Max value: {0:e}").format(self.vMax))

            ## min value
            buffer=f.read(4)
            self.vMin=struct.unpack(self.f_f, buffer)[0]
            print(("Min value: {0:e}").format(self.vMin))

            ## unnecessary properties
            buffer=f.read(4)

            ## horizontal interval
            buffer=f.read(4)
            self.hInterval=struct.unpack(self.f_f, buffer)[0]
            print(("Horizontal interval: {0:e}").format(self.hInterval))

            ## horizontal offset
            buffer=f.read(8)
            self.hOffset=struct.unpack(self.f_d, buffer)[0]
            print(("Horizontal offset: {0:e}").format(self.hOffset))

            ## unnecessary properties
            buffer=f.read(8)

            ## vertical unit
            buffer=f.read(48)
            self.vUnit=removeNull(buffer)
            print(("Vertical unit: {0:s}").format(self.vUnit))

            ## horizontal unit
            buffer=f.read(48)
            self.hUnit=removeNull(buffer)
            print(("Horizontal unit: {0:s}").format(self.hUnit))

            ## unnecessary properties
            buffer=f.read(4)

            ## Triggered time
            buffer=f.read(8)
            sec=struct.unpack(self.f_d, buffer)[0]
            sec_i=math.floor(sec)
            msec=round(1000000*(sec-sec_i))
            buffer=f.read(1)
            min=buffer[0]
            buffer=f.read(1)
            hr=buffer[0]
            buffer=f.read(1)
            day=buffer[0]
            buffer=f.read(1)
            mon=buffer[0]
            buffer=f.read(2)
            yr=struct.unpack(self.f_w, buffer)[0]
            self.time=datetime(yr, mon, day, hr, min, sec_i, msec)
            print(("Datetime: {0:s}").format(self.time.isoformat(" ")))
            buffer=f.read(2)

            ## unnecessary properties
            buffer=f.read(12)

            ## timeBase
            buffer=f.read(2)
            self.timeBase=struct.unpack(self.f_w, buffer)[0]
            print(("Time base: {0:s} / div").format(Constants.timeBases[self.timeBase]))

            ## vertical coupling
            buffer=f.read(2)
            self.vCoupling=struct.unpack(self.f_w, buffer)[0]
            print(("Vertical coupling: {0:s}").format(Constants.vCouplings[self.vCoupling]))

            ## unnecessary properties
            buffer=f.read(4)

            ## vertical gain
            buffer=f.read(2)
            self.vGain_f=struct.unpack(self.f_w, buffer)[0]
            print(("Fixed vertical gain: {0:s} / div").format(Constants.vGains[self.vGain_f]))

            ## unnecessary properties
            buffer=f.read(10)

            ## wave source
            buffer=f.read(2)
            self.source=struct.unpack(self.f_w, buffer)[0]
            print(("Wave source: {0:s}").format(Constants.sources[self.source]))

            # USERTEXT
            if self.length_UT>0:
                print("Skip USERTEXT")
                buffer=f.read(self.length_UT)

            # TRIGTIME
            if self.length_TT>0:
                print("Skip TRIGTIME")
                buffer=f.read(self.length_TT)

            # RISTIME
            if self.length_RT>0:
                print("Skip RISTIME")
                buffer=f.read(self.length_RT)

            # DATA_ARRAY_1
            print("Read DATA_ARRAY_1")
            if self.commType==0:
                self.data=np.zeros(self.numData, dtype=np.int8)
            else:
                self.data=np.zeros(self.numData, dtype=np.int16)

            dataLength=2 if self.commType==1 else 1
            for i in range(0, self.numData):
                buffer=f.read(dataLength)
                self.data[i]=struct.unpack(self.f_v, buffer)[0]

            print(("Data: {0:s}").format(repr(self.data)))









def removeNull(a):
    # return string of a, before \x00
    i=0
    while True:
        if a[i]==0:
            break
        i+=1
    return a[0:i].decode()





                    






