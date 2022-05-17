# HandleBinary_LeCroy Viewer example

import sys
import numpy as np
import pyqtgraph as pg
from lib import HandleBinary as HB


if len(sys.argv)<2:
    print("Error: file path is necessary")
    sys.exit()

filePath=sys.argv[1]
HBObj=HB.HandleBinary(filePath)

x=np.zeros(HBObj.numData, dtype=np.double)
y=np.zeros(HBObj.numData, dtype=np.double)

for i in range(0, HBObj.numData):
    x[i]=HBObj.hOffset+HBObj.hInterval*i

y=HBObj.data*HBObj.vGain+HBObj.vOffset

pg.plot(x, y, title=filePath)

pg.exec()
