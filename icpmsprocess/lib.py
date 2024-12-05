from icpmsprocess.mstypes import (
    IsotopeRatio,
    IsotopeSystem,
    PeakStripSettings,
    ReferenceMaterial,
    ReferenceValue,
)

HG204_HG202_RATIO: float = 0.2299

Pb_Pb = IsotopeSystem(
    name="Pb-Pb",
    ratios=[
        IsotopeRatio("206Pb", "204Pb"),
        IsotopeRatio("207Pb", "204Pb"),
        IsotopeRatio("208Pb", "204Pb"),
        IsotopeRatio("207Pb", "206Pb"),
        IsotopeRatio("208Pb", "206Pb"),
        IsotopeRatio("206Pb", "207Pb"),
        IsotopeRatio("208Pb", "207Pb"),
    ],
    peak_strip=PeakStripSettings(
        target_isotope="204Pb",
        known_isotope_ratio=IsotopeRatio("204Hg", "202Hg"),
        known_isotope_ratio_value=HG204_HG202_RATIO,
    ),
)


NIST610 = ReferenceMaterial(
    name="NIST SRM 610",
    values={
        "206Pb_204Pb": ReferenceValue(
            value=17.052, source="Baker et al 2004, Chem Geol"
        ),
        "207Pb_204Pb": ReferenceValue(
            value=15.515, source="Baker et al 2004, Chem Geol"
        ),
        "208Pb_204Pb": ReferenceValue(
            value=36.991, source="Baker et al 2004, Chem Geol"
        ),
        "207Pb_206Pb": ReferenceValue(
            value=0.90986, source="Baker et al 2004, Chem Geol"
        ),
        "208Pb_206Pb": ReferenceValue(
            value=2.1694, source="Baker et al 2004, Chem Geol"
        ),
        "206Pb_207Pb": ReferenceValue(
            value=17.052 / 15.515, source="calculated from Baker et al 2004, Chem Geol"
        ),
        "208Pb_207Pb": ReferenceValue(
            value=36.991 / 15.515, source="calculated from Baker et al 2004, Chem Geol"
        ),
    },
)

NIST612 = ReferenceMaterial(
    name="NIST SRM 610",
    values={
        "206Pb_204Pb": ReferenceValue(
            value=17.099, source="Baker et al 2004, Chem Geol"
        ),
        "207Pb_204Pb": ReferenceValue(
            value=15.516, source="Baker et al 2004, Chem Geol"
        ),
        "208Pb_204Pb": ReferenceValue(
            value=37.020, source="Baker et al 2004, Chem Geol"
        ),
        "207Pb_206Pb": ReferenceValue(
            value=0.90745, source="Baker et al 2004, Chem Geol"
        ),
        "208Pb_206Pb": ReferenceValue(
            value=2.1651, source="Baker et al 2004, Chem Geol"
        ),
        "206Pb_207Pb": ReferenceValue(
            value=17.099 / 15.516, source="calculated from Baker et al 2004, Chem Geol"
        ),
        "208Pb_207Pb": ReferenceValue(
            value=37.020 / 15.516, source="calculated from Baker et al 2004, Chem Geol"
        ),
    },
)
