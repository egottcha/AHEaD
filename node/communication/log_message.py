'''
Created on 2013.09.07.
'''

class LogMessage(object):
    '''
    classdocs
    '''
    
    def __init__(self, nodeId, dateTimeInMillis):
        self.nodeId = nodeId
        self.dateTimeInMillis = dateTimeInMillis
        self.data = []
