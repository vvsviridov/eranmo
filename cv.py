"""

# Ericsson OSS-RC WCDMA RAN MO Script
# Creating CV (ConfiguraionVersion) on ERBS
# reading data from csv formatted file

"""

import sys
import os
import datetime
from com.ericsson.nms.umts.ranos.cms.moscript import MibAccess
from com.ericsson.nms.umts.ranos.cms.moscript import NameValueList

datafilename = 'data.csv'
delim = ','
cvname = 'rsi'
perbs = ''

mib = MibAccess.create()

setValueList = NameValueList()
setValueList.set('configurationVersionName', cvname)
setValueList.set('identity', cvname)
setValueList.set('type', 5)
setValueList.set('operatorName', 'oper')
setValueList.set('comment', 'comment')


if os.path.isfile(datafilename):
    datafile = open(datafilename, 'r')
    for line in datafile:
        subnet, erbs, cell, bandwidth, earfcndl = line.strip().split(delim)
        if erbs != perbs:
            try:
                fdn_parts = []
                fdn_parts.append('SubNetwork=ONRM_ROOT_MO_R')
                fdn_parts.append('SubNetwork=%s' % subnet)
                fdn_parts.append('MeContext=%s' % erbs)
                fdn_parts.append('ManagedElement=1')
                fdn_parts.append('SwManagement=1')
                fdn_parts.append('ConfigurationVersion=1')
                fdn = ','.join(fdn_parts)
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, fdn
                print 'Create CV %s' % cvname
                mib.action(fdn, 'create', setValueList)
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, fdn
                print 'Set startable %s' % cvname
                mib.action(fdn, 'setStartable', setValueList)
            except Exception:
                print 'Exception:', sys.exc_info()[0], sys.exc_info()[1]
                traceBack = sys.exc_info()[2]
                print traceBack.dumpStack()
                sys.exit(-2)
        perbs = erbs
    datafile.close()
