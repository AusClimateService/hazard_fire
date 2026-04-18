import numpy as np
from xclim.indices import griffiths_drought_factor

def _griffiths_1d(pr, kbd):
    """
    Apply xclim Griffiths DF to a single grid cell (1D time series)
    """
    # xclim expects DataArray, not numpy
    import xarray as xr

    time = np.arange(pr.size)

    pr_da = xr.DataArray(pr, dims=["time"], coords={"time": time})
    kbd_da = xr.DataArray(kbd, dims=["time"], coords={"time": time})
# 🔑 CRITICAL: restore units
    pr_da.attrs["units"] = "mm/d"   # or whatever pra actually is
    kbd_da.attrs["units"] = "mm/d"

    out = griffiths_drought_factor(pr_da, kbd_da)

    return out.values.astype(np.float32)

    
import xarray as xr

def griffiths_drought_factor_dask_exact(pr, kbd):
    return xr.apply_ufunc(
        _griffiths_1d,
        pr,
        kbd,
        input_core_dims=[["time"], ["time"]],
        output_core_dims=[["time"]],
        vectorize=True,
        dask="parallelized",
        output_dtypes=[np.float32],
    )