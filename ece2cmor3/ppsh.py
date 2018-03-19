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
            lmax = 2 * msg.get_resolution() - 1
            if pp_remap_sh.sh_mapper is None:
                shtns.SHT_NO_CS_PHASE = True
                pp_remap_sh.sh_mapper = shtns.sht(lmax, lmax, 1, shtns.sht_orthonormal + shtns.SHT_NO_CS_PHASE)
                pp_remap_sh.sh_mapper.set_grid()
            if len(values.shape) == 1:
                carray = numpy.vectorize(complex)(values[0::2], values[1::2])
                self.values = numpy.roll(numpy.flipud(pp_remap_sh.sh_mapper.synth(carray)), shift=lmax + 1, axis=1)
            elif len(values.shape) == 2:
                self.values = []
                for i in range(values.shape[0]):
                    carray = numpy.vectorize(complex)(values[i, 0::2], values[i, 1::2])
                    horslice = numpy.roll(numpy.flipud(pp_remap_sh.sh_mapper.synth(carray)), shift=lmax + 1, axis=1)
                    self.values.append(horslice)
                self.values = numpy.stack(self.values)
        else:
            if len(values.shape) == 2:
                self.values = numpy.flip(values, axis=0)
            if len(values.shape) == 3:
                self.values = numpy.flip(values, axis=1)
