# HandleBinary_LeCroy command line interface (CLI) example

from lib import HandleBinary as HB

import sys

if len(sys.argv)<2:
    print("Error: file path is necessary")
    sys.exit()

filePath=sys.argv[1]
HBObj=HB.HandleBinary(filePath)
