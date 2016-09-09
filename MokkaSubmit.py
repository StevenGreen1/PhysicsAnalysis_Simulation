# Submit Mokka jobs to the grid: MokkaSubmit.py
import os
import sys
import re
import time 

from DIRAC.Core.Base import Script
Script.parseCommandLine()
from ILCDIRAC.Interfaces.API.DiracILC import  DiracILC
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import *
from ILCDIRAC.Interfaces.API.NewInterface.Applications import *

from Logic.GridTools import *
from Logic.ThreadedTools import *

#===== User Input =====

eventsToSimulate = [ 
                       { 'EventType': "ee_nunuqqqq"  , 'EventsPerFile' : 1000 , 'Energy':  1400 } 
                   ]

mokkaSteeringFile  = 'MokkaTemplate/clic_ild_cdr.steer'
detectorModel  = 'clic_ild_cdr'
jobDescription = 'PhysicsAnalysis'
eventsPerJob =  1000
maxThread = 100

# Start submission
diracInstance = DiracILC(withRepo=False)
pool = ActivePool()
threadingSemaphore = threading.Semaphore(maxThread)

# Mokka Template
base = open(mokkaSteeringFile,'r')
mokkaSteeringTemplate = base.read()
base.close()

for eventSelection in eventsToSimulate:
    eventType = eventSelection['EventType']
    eventsPerFile = eventSelection['EventsPerFile']
    energy = eventSelection['Energy']
    stdhepFormat = 'whizard_' + eventType + '_' + str(energy) + 'GeV_WhizardJobSet(.*?)\.(.*?)\.stdhep'
    stdhepFilesToProcess = GetGeneratorFiles(eventType,energy)

    for idx, stdhepFile in enumerate(stdhepFilesToProcess):
        while threading.activeCount() > (maxThread * 2):
            time.sleep(5)

        jobInfo = {}
        jobInfo['jobDescription'] = jobDescription
        jobInfo['eventsPerFile'] = eventsPerFile
        jobInfo['eventsPerJob'] = eventsPerJob
        jobInfo['stdhepFormat'] = stdhepFormat
        jobInfo['stdhepFile'] = stdhepFile
        jobInfo['eventType'] = eventType
        jobInfo['energy'] = energy
        jobInfo['detectorModel'] = detectorModel
        jobInfo['mokkaSteeringFile'] = mokkaSteeringFile
        jobInfo['diracInstance'] = diracInstance
        jobInfo['idx'] = idx

        downloadThread = threading.Thread(target=MokkaWorker, name=str(stdhepFile), args=(threadingSemaphore, pool, jobInfo))
        downloadThread.start()

currentThread = threading.currentThread()
for thread in threading.enumerate():
    if thread is currentThread:
        continue
    thread.join(60)

