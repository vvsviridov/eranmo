'''

# Ericsson OSS-RC WCDMA RAN MO Script
# Setting EARFCN value and channel bandwidth on ERBS
# reading data from csv formatted file

'''


import sys
import os
import datetime
from com.ericsson.nms.umts.ranos.cms.moscript import MibAccess
from com.ericsson.nms.umts.ranos.cms.moscript import NameValueList

datafilename = 'data.csv'
delim = ','

mib = MibAccess.create()
attrGet = []
attrGet.append('administrativeState')
attrGet.append('operationalState')
attrGet.append('dlChannelBandwidth')
attrGet.append('ulChannelBandwidth')
attrGet.append('earfcndl')
attrGet.append('earfcnul')

setValueList = NameValueList()
setValueList.set('administrativeState', 0)

debValueList = NameValueList()
attrAct = NameValueList()

if os.path.isfile(datafilename):
    with open(datafilename, 'r') as datafile:
        for line in datafile:
            subnet, erbs, cell, bandwidth, earfcndl = line.strip().split(delim)
        #   ^ ---           csv format        --- ^
            fdn_parts = {'SubNetwork': subnet,
                         'MeContext': erbs,
                         'ManagedElement': '1',
                         'ENodeBFunction': '1',
                         'EUtranCellFDD': cell}
            try:
                fdn = ','.join(['SubNetwork=ONRM_ROOT_MO_R'] +
                               ['%s=%s' % (k, v) for k, v in fdn_parts.items()]
                               )
                getValueList = mib.getAttributes(fdn, attrGet)
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, fdn
                print 'Attributes before are = ', getValueList.toString()
                setValueList.set('dlChannelBandwidth', int(bandwidth))
                setValueList.set('ulChannelBandwidth', int(bandwidth))
                print 'Attributes to set are = ', setValueList.toString()
                print 'Setting earfcn to', earfcndl
                mib.beginTransaction(60)
                mib.setAttributes(fdn, setValueList)
                attrAct.set('earfcn', int(earfcndl))
                mib.action(fdn, 'changeFrequency', attrAct)
                mib.commitTransaction()
                current_cell_state = getValueList.get('administrativeState')
                debValueList.set('administrativeState', current_cell_state)
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, 'Return to previous state = ', \
                      debValueList.toString(), '\n\n'
                mib.beginTransaction(60)
                mib.setAttributes(fdn, debValueList)
                mib.commitTransaction()
            except Exception:
                mib.rollbackTransaction()
                print 'Exception:', sys.exc_info()[0], sys.exc_info()[1]
                traceBack = sys.exc_info()[2]
                print traceBack.dumpStack()
                sys.exit(-2)
