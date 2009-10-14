
#Quick little script to create an array of test data for raDecStr
from math import pi

def printLine(raDeg, decDeg, raStr, decStr):
    raRad = raDeg * pi/180.
    decRad = decDeg * pi/180.
    
    print '[%.8f, %.8f, %.8f, %.8f, "%s", "%s"],' %   \
        (raDeg, decDeg, raRad, decRad, raStr, decStr)
    
    
def goodRa():    
    raDeg = [0, 1/3600., .004166667, 1/60., 1., 15.]
    raStr = ["00:00:00.00", "00:00:00.07", "00:00:01.00", "00:00:04.00", "00:04:00.00", "01:00:00.00"]

    assert len(raDeg) == len(raStr), "raDeg and raStr must be of same len"

    decDeg = 0
    for i in range(len(raDeg)):
        printLine(raDeg[i], decDeg, raStr[i], "+00:00:00.00")    
    

def goodDec():    
    decDeg = [1/3600., 1/60., 1., 15.]
    decStr = ["00:00:01.00", "00:01:00.00", "01:00:00.00", "15:00:00.00"]

    assert(len(decDeg) == len(decStr), "decDeg and decStr must be of same len")

    raDeg = 0
    for i in range(len(decDeg)):
        printLine(raDeg, decDeg[i], "00:00:00.00", decStr[i])    
        printLine(raDeg, decDeg[i], "00:00:00.00", "+"+decStr[i])    
        printLine(raDeg, -1*decDeg[i], "00:00:00.00", "-"+decStr[i])    
    


def main():
    goodRa()
    goodDec()
