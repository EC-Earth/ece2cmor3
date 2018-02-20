import numpy
import shtns

from ece2cmor3 import ppop


class pp_remap_sh(ppop.post_proc_operator):

    sh_mapper = None

    def __init__(self):
        super(pp_remap_sh, self).__init__()

    def fill_cache(self, msg):
        values = msg.get_values()
        if msg.is_spectral():
            if pp_remap_sh.sh_mapper is None:
                lmax = 2 * msg.get_resolution() - 1
                shtns.SHT_NO_CS_PHASE = True
                pp_remap_sh.sh_mapper = shtns.sht(lmax, lmax, 1, shtns.sht_orthonormal + shtns.SHT_NO_CS_PHASE)
            if len(values.shape) == 1:
                self.values = numpy.flipud(
                    pp_remap_sh.sh_mapper.synth(numpy.vectorize(complex)(values[0::2], values[1::2])))
            elif len(values.shape) == 2:
                self.values = numpy.flip(
                    pp_remap_sh.sh_mapper.synth(numpy.vectorize(complex)(values[:, 0::2], values[:, 1::2])), axis=1)
        else:
            if len(values.shape) == 2:
                shift = values.shape[1]/2
                self.values = numpy.roll(numpy.flip(values, axis=0), shift, axis=1)
            if len(values.shape) == 3:
                shift = values.shape[2]/2
                self.values = numpy.roll(numpy.flip(values, axis=1), shift, axis=2)
