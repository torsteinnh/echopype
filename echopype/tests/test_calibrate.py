from pathlib import Path
import numpy as np
import pandas as pd
from ..convert import Convert
from ..process import EchoDataNew

ek60_raw_path = './echopype/test_data/ek60/DY1801_EK60-D20180211-T164025.raw'     # Constant ranges
ek60_csv_path = Path('./echopype/test_data/ek60/from_echoview/')


def test_get_Sv_ek60_echoview():
    # Convert file
    c = Convert(ek60_raw_path, model='EK60')
    c.to_netcdf(overwrite=True)

    # Calibrate to get Sv
    echodata = EchoDataNew(raw_path=c.output_file)
    echodata.get_Sv()

    # Compare with EchoView outputs
    channels = []
    for freq in [18, 38, 70, 120, 200]:
        fname = str(ek60_csv_path.joinpath('DY1801_EK60-D20180211-T164025-Sv%d.csv' % freq))
        channels.append(pd.read_csv(fname, header=None, skiprows=[0]).iloc[:, 13:])
    test_Sv = np.stack(channels)

    # Echoview data is shifted by 1 sample along range (missing the first sample)
    assert np.allclose(test_Sv[:, :, 7:],
                       echodata.Sv.Sv.isel(ping_time=slice(None, 10), range_bin=slice(8, None)), atol=1e-8)

    Path(c.output_file).unlink()
