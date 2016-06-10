# Submit Mokka jobs to the grid: MokkaSubmit.py
import os
import sys
import re

from DIRAC.Core.Base import Script
Script.parseCommandLine()
from ILCDIRAC.Interfaces.API.DiracILC import  DiracILC
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import *
from ILCDIRAC.Interfaces.API.NewInterface.Applications import *

from Logic.GridTools import *

#===== User Input =====

eventsToSimulate = [ 
                       { 'EventType': "ee_nunuww_nunuqqqq"  , 'EventsPerFile' : 1000 , 'Energies':  ['1400'] }, 
                       { 'EventType': "ee_nunuzz_nunuqqqq"  , 'EventsPerFile' : 1000 , 'Energies':  ['1400'] } 
                   ]

baseXmlFile  = 'MokkaTemplate/clic_ild_cdr.steer'
detectorModel  = 'clic_ild_cdr'
jobDescription = 'PhysicsAnalysis'
eventsPerJob =  100

# Start submission
JobIdentificationString = 'PhysicsAnalysis_' + detectorModel
diracInstance = DiracILC(withRepo=True,repoLocation="%s.cfg" %( JobIdentificationString))

for eventSelection in eventsToSimulate:
    eventType = eventSelection['EventType']
    eventsPerFile = eventSelection['EventsPerFile']
    for energy in eventSelection['Energies']:
        stdhepFormat = 'whizard_' + eventType + '_' + energy + 'GeV.(.*?).stdhep'
        stdhepFilesToProcess = GetGeneratorFiles(eventType,energy)
        for stdhepFile in stdhepFilesToProcess:
            for startEvent in xrange(0, eventsPerFile, eventsPerJob):
                matchObj = re.match(stdhepFormat, os.path.basename(stdhepFile), re.M|re.I) # "whizard_ee_nunuww_nunuqqqq_1400GeV.100.stdhep"
                generatorSerialNumber = ''

                if matchObj:
                    generatorSerialNumber = matchObj.group(1)
                else:
                    print 'Wrong stdhep format.  Please check.'

                print 'Submitting ' + eventType + ', ' + energy + 'GeV jobs.  Detector model ' + detectorModel + '.  Generator serial number ' + str(generatorSerialNumber) + '.  Start event number ' + str(startEvent) + '.'  

                description = eventType + '_' + str(energy) + 'GeV_GeneratorSerialNumber_' + str(generatorSerialNumber) 
                outputFile = 'MokkaSim_Detector_Model_' + detectorModel + '_' + description + '_' + str(eventsPerJob) + '_' + str(startEvent) + '.slcio'
                outputPath = '/' + jobDescription + '/MokkaJobs/Detector_Model_' + detectorModel + '/' + eventType + '/' + str(energy) + 'GeV'

                lfn = '/ilc/user/s/sgreen/' + outputPath + '/' + outputFile
                if DoesFileExist(lfn):
                    continue

                mokkaSteeringTemplate = ''
                base = open(baseXmlFile,'r')
                mokkaSteeringTemplate = base.read()
                base.close()
                mokkaSteeringTemplate = re.sub('LcioOutputFile',outputFile,mokkaSteeringTemplate)
                mokkaSteeringTemplate = re.sub('StartEventNumber',str(startEvent),mokkaSteeringTemplate)

                with open("MokkaSteering.steer" ,"w") as steeringFile:
                    steeringFile.write(mokkaSteeringTemplate)

                MokkaApplication = Mokka()
                MokkaApplication.setVersion('0706P08') # Version info for offical CLIC productions as of 8-6-16
                MokkaApplication.setSteeringFile('MokkaSteering.steer')
                MokkaApplication.setNumberOfEvents(eventsPerJob)
                MokkaApplication.setStartFrom(startEvent)
                MokkaApplication.setDbSlice('LFN:/ilc/user/s/sgreen/PhysicsAnalysis/MokkaJobs/CLICMokkaDatabase/CLICMokkaDB.sql')

                job = UserJob()
                job.setJobGroup(jobDescription)
                job.setOutputSandbox( ["*.log", "*.gear", "*.mac", "*.steer", "*.xml" ] )
                job.setOutputData(outputFile, OutputPath=outputPath)
                job.setInputData(stdhepFile)
                jobDetailedName = jobDescription + '_' + detectorModel + '_' + eventType + '_' + energy + 'GeV_GeneratorSerialNumber_' + str(generatorSerialNumber) + '_' +  str(eventsPerJob) + '_' + str(startEvent) 
                job.setName(jobDetailedName)
                job.setBannedSites(['LCG.IN2P3-CC.fr','LCG.IN2P3-IRES.fr','LCG.KEK.jp','OSG.PNNL.us','OSG.CIT.us'])

                res = job.append(MokkaApplication)
                if not res['OK']:
                    print res['Message']
                    exit()
                job.dontPromptMe()
                job.submit(diracInstance)
                os.system('rm *.cfg')

# Tidy Up
os.system('rm MokkaSteering.steer')
