from cmor_source import cmor_source

class cmor_task(object):

    def __init__(self,source_,target_):
        if(isinstance(source_,cmor_source)):
            self.realm=source_.realm
        else:
            raise Exception("Invalid source type argument for cmor-task:",source_)
        source=source_
        target=target_
        postproc=None
        cmorize=None

    def execute(self):
        if(postproc!=None):
            postproc(self.source)
        if(cmorize!=None):
            cmorize(self.source,self.target)
