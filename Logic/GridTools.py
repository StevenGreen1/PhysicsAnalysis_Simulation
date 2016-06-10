import os

### ----------------------------------------------------------------------------------------------------

def GetGeneratorFiles(eventType, energy):
    jobDescription = 'StdHep'

    stdhepFiles = []
    os.system('dirac-ilc-find-in-FC /ilc JobDescription="' + jobDescription + '" Energy=' + str(energy) + ' EvtType="' + eventType + '" > tmp.txt')
    with open('tmp.txt') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            line = line.strip()
            stdhepFiles.append(line)
    os.system('rm tmp.txt')
    return stdhepFiles

### ----------------------------------------------------------------------------------------------------

def DoesFileExist(lfn):
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager
    dm = DataManager()
    result = dm.getActiveReplicas(lfn)
    if result[('Value')][('Successful')]:
        return True
    else:
        return False

### ----------------------------------------------------------------------------------------------------
