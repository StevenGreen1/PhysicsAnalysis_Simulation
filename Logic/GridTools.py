import os

### ----------------------------------------------------------------------------------------------------

def GetGeneratorFiles(eventType, energy):
    jobDescription = 'PhysicsAnalysis'

    stdhepFiles = []
    os.system('dirac-ilc-find-in-FC /ilc JobDescription="' + jobDescription + '" Energy=' + str(energy) + ' EvtType="' + eventType + '" > tmp.txt')
    with open('tmp.txt') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            line = line.strip()
            if 'WhizardJobSet' in line:
                stdhepFiles.append(line)
    return stdhepFiles

### ----------------------------------------------------------------------------------------------------

def DoesFileExist(lfn):
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager
    dm = DataManager()
    result = dm.getActiveReplicas(lfn)
    if not result['OK']:
        print "ERROR",result['Message']
        return False
    if lfn in result['Value']['Successful']:
        return True
    else:
        return False

### ----------------------------------------------------------------------------------------------------
