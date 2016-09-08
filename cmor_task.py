import cmor_source
import cmor_target

# Cmorization task class, containing source and targets.
# TODO: Add postprocessing functor to this object.

class cmor_task(object):

    def __init__(self,source_,target_):
        if(not isinstance(source_,cmor_source)):
            raise Exception("Invalid source argument type for cmor task:",source_)
        if(not isinstance(target_,cmor_target)):
            raise Exception("Invalid target argument type for cmor task:",target_)
        source=source_
        target=target_
