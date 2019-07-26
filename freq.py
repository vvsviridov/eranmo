'''

# Ericsson OSS-RC WCDMA RAN MO Script
# Setting EARFCN value and channel bandwidth on ERBS
# reading data from csv formatted file

'''


import sys
import os
import datetime
import traceBack
from com.ericsson.nms.umts.ranos.cms.moscript import MibAccess
from com.ericsson.nms.umts.ranos.cms.moscript import NameValueList


def transaction_wrapper(func):
    def inner1(*args, **kwargs):
        try:
            mib.beginTransaction(60)
            returned_value = func(*args, **kwargs)
            mib.commitTransaction()
        except Exception:
            mib.rollbackTransaction()
            print 'Exception:', sys.exc_info()[0], sys.exc_info()[1]
            traceBack = sys.exc_info()[2]
            print traceBack.dumpStack()
            sys.exit(-2)
        return returned_value
    return inner1


def prepareNameValue(func):
    def inner2(*args, **kwargs):
        paramNameValueList = NameValueList()
        for k, v in kwargs:
            paramNameValueList.set(k, v)
        print 'Attributes to set are = ', paramNameValueList.toString()
        args.append(paramNameValueList)
        func(*args)
    return inner2


@transaction_wrapper
def get_attributes(mib, fdn, nmValueList):
    return mib.getAttributes(fdn, nmValueList)


@transaction_wrapper
@prepareNameValue
def set_attributes(mib, fdn, nmValueList):
    mib.setAttributes(fdn, nmValueList)


@transaction_wrapper
@prepareNameValue
def execute_action(mib, fdn, actionName, nmValueList):
    mib.action(fdn, actionName, nmValueList)


def main():
    datafilename = 'data.csv'
    delim = ','
    MIB = MibAccess.create()
    if os.path.isfile(datafilename):
        with open(datafilename, 'r') as datafile:
            for line in datafile:
                subnet, erbs, cell, bandwidth, earfcndl \
                    = line.strip().split(delim)
            #   ^ ---           csv format        --- ^
                fdn_parts = {'SubNetwork': subnet,
                             'MeContext': erbs,
                             'ManagedElement': '1',
                             'ENodeBFunction': '1',
                             'EUtranCellFDD': cell}
                FDN = ','.join(['SubNetwork=ONRM_ROOT_MO_R'] +
                               ['%s=%s' % (k, v) for k, v in fdn_parts.items()]
                               )
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, fdn
                attrGet = []
                attrGet.append('administrativeState')
                attrGet.append('operationalState')
                attrGet.append('dlChannelBandwidth')
                attrGet.append('ulChannelBandwidth')
                attrGet.append('earfcndl')
                attrGet.append('earfcnul')
                getValueList = get_attributes(MIB, FDN, attrGet)
                current_cell_state = getValueList.get('administrativeState')
                set_attributes(MIB,
                               FDN,
                               administrativeState=0
                               dlChannelBandwidth=int(bandwidth),
                               ulChannelBandwidth=int(bandwidth)
                               )
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, fdn
                print 'Execute action = changeFrequency'
                execute_action(MIB,
                               FDN,
                               'changeFrequency',
                               earfcn=int(earfcndl)
                               )
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, fdn
                print 'Return to previous state = ', current_cell_state
                set_attributes(MIB,
                               FDN,
                               administrativeState=current_cell_state
                               )


if __name__ == '__main__':
    main()
