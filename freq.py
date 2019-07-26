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


def transaction_wrapper(func):

    """
    Wrapping called MIB methods into transaction

    Arguments:
        func {function} -- function to be wrapped

    Returns:
        [function] -- wrapped function
    """

    def inner1(*args, **kwargs):
        try:
            mib.beginTransaction(60)
            returned_value = func(*args, **kwargs)
            mib.commitTransaction()
        except Exception:
            mib.rollbackTransaction()
            print 'Exception:', sys.exc_info()[0], sys.exc_info()[1]
        return returned_value
    return inner1


def prepareNameValue(func):

    """
    Wrapper for preparing NameValueList() parameter
    for passing to wrapped function

    Arguments:
        func {function} -- function to be wrapped

    Returns:
        None
    """

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

    """
    Function for reading parameter's values from the network

    Arguments:
        mib {object} -- OSS MIB object to be called
        fdn {string} -- Object's FDN for ex.:
            SubNetwork=ONRM_ROOT_MO_R,SubNetwork=ENODEBS,MeContext=ERBS1,\
                ManagedElement=1,ENodeBFunction=1,EUtranCellFDD=FDDCELL1
        nmValueList {List} -- List with parameters for reading their values

    Returns:
        [NameValueList] -- NameValueList Object \
            with parameters and readed values
    """

    return mib.getAttributes(fdn, nmValueList)


@transaction_wrapper
@prepareNameValue
def set_attributes(mib, fdn, nmValueList):

    """
    Function for setting parameter's values to the network

    Arguments:
        mib {object} -- OSS MIB object to be called
        fdn {string} -- Object's FDN for ex.:
            SubNetwork=ONRM_ROOT_MO_R,SubNetwork=ENODEBS,MeContext=ERBS1,\
                ManagedElement=1,ENodeBFunction=1,EUtranCellFDD=FDDCELL1
        nmValueList {NameValueList} -- NameValueList Object \
            with parameters and setted values
    """

    mib.setAttributes(fdn, nmValueList)


@transaction_wrapper
@prepareNameValue
def execute_action(mib, fdn, actionName, nmValueList):
    """
    Function for executing "action" on the network's objects

    Arguments:
        mib {object} -- OSS MIB object to be called
        fdn {string} -- Object's FDN for ex.:
            SubNetwork=ONRM_ROOT_MO_R,SubNetwork=ENODEBS,MeContext=ERBS1,\
                ManagedElement=1,ENodeBFunction=1,EUtranCellFDD=FDDCELL1
        actionName {string} -- Action's name
        nmValueList {NameValueList} -- NameValueList Object \
            with parameters and setted values
    """

    mib.action(fdn, actionName, nmValueList)


def main():
    """
    Program's main function
    It reads data from csv file formatted as
    subnet,erbs,cell,bandwidth,earfcndl
    There are <subnet,erbs,cell> for building FDN
    and <bandwidth,earfcndl> values for setting
    dlChannelBandwidth, ulChannelBandwidth,
    executing action <changeFrequency> for changing
    EARFCN
    """

    datafilename = 'data.csv'
    delim = ','
    MIB = MibAccess.create()
    if os.path.isfile(datafilename):
        with open(datafilename, 'r') as datafile:
            for line in datafile:
                subnet, erbs, cell, bandwidth, earfcndl \
                    = line.strip().split(delim)
                fdn_parts = {'SubNetwork': subnet,
                             'MeContext': erbs,
                             'ManagedElement': '1',
                             'ENodeBFunction': '1',
                             'EUtranCellFDD': cell}
                FDN = ','.join(['SubNetwork=ONRM_ROOT_MO_R'] +
                               ['%s=%s' % (k, v) for k, v in fdn_parts.items()]
                               )
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, FDN
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
                               administrativeState=0,
                               dlChannelBandwidth=int(bandwidth),
                               ulChannelBandwidth=int(bandwidth)
                               )
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, FDN
                print 'Execute action = changeFrequency'
                execute_action(MIB,
                               FDN,
                               'changeFrequency',
                               earfcn=int(earfcndl)
                               )
                dt = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
                print 'OP_PROGRESS: ', dt, FDN
                print 'Return to previous state = ', current_cell_state
                set_attributes(MIB,
                               FDN,
                               administrativeState=current_cell_state
                               )


if __name__ == '__main__':
    main()
