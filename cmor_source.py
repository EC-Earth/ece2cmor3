class cmor_source(object):
    def __init__(self):
        self.grid=None
        self.dims=0
        self.realm=None

class grib_code:
    def __init__(self,var_id_,tab_id_):
        self.var_id=var_id_
        self.tab_id=tab_id_
    def __eq__(self,other):
        return self.var_id==other.var_id and self.tab_id==other.tab_id

class ifs_source(cmor_source):

    #TODO: Put these in a json-file
    grib_codes_3D=[grib_code(3,128),
                   grib_code(53,128),
                   grib_code(54,128),
                   grib_code(60,128),
                   grib_code(75,128),
                   grib_code(76,128),
                   grib_code(129,128),
                   grib_code(130,128),
                   grib_code(131,128),
                   grib_code(132,128),
                   grib_code(133,128),
                   grib_code(135,128),
                   grib_code(138,128),
                   grib_code(155,128),
                   grib_code(157,128),
                   grib_code(203,128),
                   grib_code(246,128),
                   grib_code(247,128),
                   grib_code(248,128)]

    grib_codes_2D_dyn=[grib_code(129,128),
                       grib_code(134,128),
                       grib_code(152,128)]

    grib_codes_2D_phy=[grib_code(8,128),
                       grib_code(9,128),
                       grib_code(31,128),
                       grib_code(32,128),
                       grib_code(33,128),
                       grib_code(34,128),
                       grib_code(35,128),
                       grib_code(36,128),
                       grib_code(37,128),
                       grib_code(38,128),
                       grib_code(39,128),
                       grib_code(40,128),
                       grib_code(41,128),
                       grib_code(42,128),
                       grib_code(43,128),
                       grib_code(44,128),
                       grib_code(45,128),
                       grib_code(49,128),
                       grib_code(50,128),
                       grib_code(57,128),
                       grib_code(58,128),
                       grib_code(78,128),
                       grib_code(79,128),
                       grib_code(121,128),
                       grib_code(122,128),
                       grib_code(123,128),
                       grib_code(124,128),
                       grib_code(125,128),
                       grib_code(129,128),
                       grib_code(136,128),
                       grib_code(137,128),
                       grib_code(139,128),
                       grib_code(141,128),
                       grib_code(142,128),
                       grib_code(143,128),
                       grib_code(144,128),
                       grib_code(145,128),
                       grib_code(146,128),
                       grib_code(147,128),
                       grib_code(148,128),
                       grib_code(151,128),
                       grib_code(159,128),
                       grib_code(164,128),
                       grib_code(165,128),
                       grib_code(166,128),
                       grib_code(167,128),
                       grib_code(168,128),
                       grib_code(169,128),
                       grib_code(170,128),
                       grib_code(172,128),
                       grib_code(173,128),
                       grib_code(174,128),
                       grib_code(175,128),
                       grib_code(176,128),
                       grib_code(177,128),
                       grib_code(178,128),
                       grib_code(179,128),
                       grib_code(180,128),
                       grib_code(181,128),
                       grib_code(182,128),
                       grib_code(183,128),
                       grib_code(186,128),
                       grib_code(187,128),
                       grib_code(188,128),
                       grib_code(189,128),
                       grib_code(195,128),
                       grib_code(196,128),
                       grib_code(197,128),
                       grib_code(198,128),
                       grib_code(201,128),
                       grib_code(202,128),
                       grib_code(205,128),
                       grib_code(206,128),
                       grib_code(208,128),
                       grib_code(209,128),
                       grib_code(210,128),
                       grib_code(211,128),
                       grib_code(212,128),
                       grib_code(213,128),
                       grib_code(228,128),
                       grib_code(229,128),
                       grib_code(230,128),
                       grib_code(231,128),
                       grib_code(232,128),
                       grib_code(234,128),
                       grib_code(235,128),
                       grib_code(236,128),
                       grib_code(238,128),
                       grib_code(243,128),
                       grib_code(244,128),
                       grib_code(245,128),
                       grib_code(1,228),
                       grib_code(8,228),
                       grib_code(9,228),
                       grib_code(10,228),
                       grib_code(11,228),
                       grib_code(12,228),
                       grib_code(13,228),
                       grib_code(14,228),
                       grib_code(24,228),
                       grib_code(89,228),
                       grib_code(90,228),
                       grib_code(246,228),
                       grib_code(247,228),
                       grib_code(121,260),
                       grib_code(123,260)]

    grib_codes_extra=[grib_code(91,128),
                      grib_code(92,128),
                      grib_code(93,128),
                      grib_code(94,128),
                      grib_code(95,128),
                      grib_code(96,128),
                      grib_code(97,128),
                      grib_code(98,128),
                      grib_code(99,128),
                      grib_code(100,128),
                      grib_code(101,128),
                      grib_code(102,128),
                      grib_code(103,128),
                      grib_code(104,128),
                      grib_code(105,128),
                      grib_code(106,128),
                      grib_code(107,128),
                      grib_code(108,128),
                      grib_code(109,128),
                      grib_code(110,128),
                      grib_code(111,128),
                      grib_code(112,128),
                      grib_code(113,128),
                      grib_code(114,128)]

    grib_codes=grib_codes_3D+grib_codes_2D_phy+grib_codes_2D_phy+grib_codes_extra

    def __init__(self,code):
        if(not code in ifs_source.grib_codes):
            raise Exception("Unknown grib code passed to IFS source parameter constructor:",code)
        self.code__=code
        if(code in ifs_source.grib_codes_3D):
            self.grid="spec_grid"
            self.dims=3
        else:
            self.grid="pos_grid"
            self.dims=2
        self.realm="atmos"
