import os
import re
import sys
import random
import threading

from ILCDIRAC.Interfaces.API.DiracILC import  DiracILC
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import *
from ILCDIRAC.Interfaces.API.NewInterface.Applications import *
from DIRAC.Core.Base import Script
Script.parseCommandLine()
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

from GridTools import *

### ----------------------------------------------------------------------------------------------------
### Start of SubmitMokkaJob function
### ----------------------------------------------------------------------------------------------------

def SubmitMokkaJob(jobInfo):
    #########################
    # Unpack job information
    #########################
    jobDescription = jobInfo['jobDescription']
    eventsPerFile = jobInfo['eventsPerFile']
    eventsPerJob = jobInfo['eventsPerJob'] 
    stdhepFormat = jobInfo['stdhepFormat']
    stdhepFile = jobInfo['stdhepFile']
    eventType = jobInfo['eventType'] 
    energy = jobInfo['energy']
    detectorModel = jobInfo['detectorModel'] 
    mokkaSteeringFile = jobInfo['mokkaSteeringFile'] 
    diracInstance = jobInfo['diracInstance'] 
    idx = jobInfo['idx']

    base = open(mokkaSteeringFile,'r')
    mokkaSteeringTemplateContent = base.read()
    base.close()

    matchObj = re.match(stdhepFormat, os.path.basename(stdhepFile), re.M|re.I) # "whizard_ee_nunuww_nunuqqqq_1400GeV.100.stdhep"
    generatorSerialNumber = ''

    if matchObj:
        jobSet = int(matchObj.group(1))
        runNumber = int(matchObj.group(2))
        generatorSerialNumber = str((1000*jobSet)+runNumber)
    else:
        print 'Wrong stdhep format.  Please check.'
        return

    for startEvent in xrange(0, eventsPerFile, eventsPerJob):
        print 'Checking ' + eventType + ', ' + str(energy) + 'GeV jobs.  Detector model ' + detectorModel + '.  Generator serial number ' + str(generatorSerialNumber) + '.  Start event number ' + str(startEvent) + '.'
        description = eventType + '_' + str(energy) + 'GeV_GeneratorSerialNumber_' + str(generatorSerialNumber)
        outputFile = 'MokkaSim_Detector_Model_' + detectorModel + '_' + description + '_' + str(eventsPerJob) + '_' + str(startEvent) + '.slcio'
        outputPath = '/' + jobDescription + '/MokkaJobs/Detector_Model_' + detectorModel + '/' + eventType + '/' + str(energy) + 'GeV'

        #########################
        # Check if output exists
        #########################
        lfn = '/ilc/user/s/sgreen/' + outputPath + '/' + outputFile
        if DoesFileExist(lfn):
            continue

        #########################
        # Edit Mokka Template 
        #########################
        mokkaSteeringContent = mokkaSteeringTemplateContent
        mokkaSteeringContent = re.sub('LcioOutputFile',outputFile,mokkaSteeringContent)
        mokkaSteeringContent = re.sub('StartEventNumber',str(startEvent),mokkaSteeringContent)

        mokkaSteeringFilename = 'MokkaSteering_' + eventType + '_' + str(idx) + '_' + str(startEvent) + '.steer'
        with open(mokkaSteeringFilename ,'w') as steeringFile:
            steeringFile.write(mokkaSteeringContent)

        #########################
        # Mokka Application
        #########################
        MokkaApplication = Mokka()
        MokkaApplication.setVersion('0706P08') # Version info for offical CLIC productions as of 8-6-16
        MokkaApplication.setSteeringFile(mokkaSteeringFilename)
        MokkaApplication.setNumberOfEvents(eventsPerJob)
        MokkaApplication.setStartFrom(startEvent)
        MokkaApplication.setDbSlice('LFN:/ilc/user/s/sgreen/PhysicsAnalysis/MokkaJobs/CLICMokkaDatabase/CLICMokkaDB.sql')

        #########################
        # User Job Settings
        #########################
        job = UserJob()
        job.setJobGroup(jobDescription)
        job.setOutputSandbox( ["*.log", "*.gear", "*.mac", "*.steer", "*.xml" ] )
        job.setOutputData(outputFile, OutputPath=outputPath)
        job.setInputData(stdhepFile)
        jobDetailedName = jobDescription + '_' + detectorModel + '_' + eventType + '_' + str(energy) + 'GeV_GeneratorSerialNumber_' + str(generatorSerialNumber) + '_' +  str(eventsPerJob) + '_' + str(startEvent)
        job.setName(jobDetailedName)
        job.setBannedSites(['LCG.IN2P3-CC.fr','LCG.IN2P3-IRES.fr','LCG.KEK.jp','OSG.PNNL.us','OSG.CIT.us','LCG.LAPP.fr','LCG.UKI-LT2-IC-HEP.uk','LCG.Tau.il','LCG.Weizmann.il','OSG.BNL.us'])
#        job.setCPUTime(43200) # Mokka jobs take a long time so set no limit. 

        res = job.append(MokkaApplication)
        if not res['OK']:
            print res['Message']
            exit()

        print 'Submitting ' + eventType + ', ' + str(energy) + 'GeV jobs.  Detector model ' + detectorModel + '.  Generator serial number ' + str(generatorSerialNumber) + '.  Start event number ' + str(startEvent) + '.'

        job.dontPromptMe()
        job.submit(diracInstance)
        os.system('rm ' + mokkaSteeringFilename)
    print 'Job(s) submitted to grid.'

### ----------------------------------------------------------------------------------------------------
### End of SubmitMokkaJob function
### ----------------------------------------------------------------------------------------------------
### Start of MokkaWorker function
### ----------------------------------------------------------------------------------------------------

def MokkaWorker(threadingSemaphore, pool, jobInfo):
    with threadingSemaphore:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        SubmitMokkaJob(jobInfo)
        pool.makeInactive(name)

### ----------------------------------------------------------------------------------------------------
### End of MokkaWorker function
### ----------------------------------------------------------------------------------------------------
### Start of ActivePool function
### ----------------------------------------------------------------------------------------------------

class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)

### ----------------------------------------------------------------------------------------------------
### End of ActivePool function
### ----------------------------------------------------------------------------------------------------


