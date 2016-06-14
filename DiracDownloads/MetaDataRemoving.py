import os

from DIRAC.Core.Base import Script
Script.parseCommandLine()
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

jobDescription = 'PhysicsAnalysis'
fileType = 'Sim'
detModel = 'clic_ild_cdr'

eventsToSimulate = [
                       { 'Process': 'ee_nunuww_nunuqqqq', 'Energies': [1400] },
                       { 'Process': 'ee_nunuzz_nunuqqqq', 'Energies': [1400] }
                   ]

fc = FileCatalogClient()

for eventSelection in eventsToSimulate:
    process = eventSelection['Process']
    for energy in eventSelection['Energies']:
        path = '/ilc/user/s/sgreen/' + jobDescription + '/MokkaJobs/Detector_Model_' + str(detModel) + '/' + process + '/' + str(energy) + 'GeV'
        metadata = ['Energy','EvtType','JobDescription','MokkaJobNumber','Type']
        metaDict = {path:metadata}
        result = fc.removeMetadata(metaDict)