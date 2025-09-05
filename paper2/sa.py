"""Sensitivity analysis functions."""
# Code for Sensitivity Analysis
#
# xarray compatible


import numpy as np
from xarray import apply_ufunc
import xarray as xr
import pandas as pd

from scipy.stats import kstest, gamma, lognorm
from scipy.stats import sobol_indices, uniform, beta, gamma, lognorm, invgauss

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.inspection import permutation_importance



## Fitting PDF code --------

# Fit beta equation to the data that returns (a, b, loc, scale)
def _fit_beta_1d(ts):
    ts = ts[~np.isnan(ts)]  # mask NaNs
    if len(ts) < 5:
        return np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan ])
    try:
        a,b,loc,scale=beta.fit(ts)
        D, p = kstest(ts, 'beta', args=(a, b, loc, scale))
        return np.array([a,b,loc,scale,D,p])
    except Exception:
        return np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan ])


# Fit gamma equation to the data that returns (a,  loc, scale)
def _fit_gamma_1d(ts):
    ts = ts[~np.isnan(ts)]  # mask NaNs
#    amin=ts.min()
#    ts=ts-amin  ##
    if len(ts) < 4:
        return np.array([ np.nan, np.nan, np.nan, np.nan, np.nan ])
    try:
        a,loc, scale = gamma.fit(ts)
        D, p = kstest(ts, 'gamma', args=(a, loc, scale))
        return np.array([a,loc,scale,D,p])
    except Exception:
        return np.array([ np.nan, np.nan, np.nan, np.nan, np.nan ])

# Fit lognorm equation to the data that returns (a,  loc, scale)
def _fit_lognorm_1d(ts):
    ts = ts[~np.isnan(ts)]  # mask NaNs
    if len(ts) < 4:
        return np.array([ np.nan, np.nan, np.nan, np.nan, np.nan ])
    try:
        a,loc, scale = lognorm.fit(ts)  #, floc=0)
        D, p = kstest(ts, 'lognorm', args=(a, loc, scale))
        return np.array([a,loc,scale,D,p])
    except Exception:
        return np.array([ np.nan, np.nan, np.nan, np.nan, np.nan ])
        
# Fit lognorm equation to the data that returns (a, loc, scale)
def _fit_invgauss_1d(ts):
    ts = ts[~np.isnan(ts)]  # mask NaNs
    if len(ts) < 4:
        return np.array([ np.nan, np.nan, np.nan, np.nan, np.nan ])
    try:
        a,loc, scale = invgauss.fit(ts)  #, floc=0)
        D, p = kstest(ts, 'invgauss', args=(a, loc, scale))
        return np.array([a,loc,scale,D,p])
    except Exception:
        return np.array([ np.nan, np.nan, np.nan, np.nan, np.nan ])

# Wrap into apply_ufunc
def fit_beta(a):
    fitted = apply_ufunc(
        _fit_beta_1d,
        a,
        input_core_dims=[["time"]],
        output_core_dims=[["parameter"]],
        output_sizes={"parameter": 6},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
    )

    fitted= fitted.assign_coords(parameter=["a", "b", "loc", "scale","KS-fit","p-value"])
    fitted.name = "beta_params"
    return fitted
#fitted.sel(parameter="a").values

# Wrap into apply_ufunc
def fit_gamma(a):
    fitted = apply_ufunc(
        _fit_gamma_1d,
        a,
        input_core_dims=[["time"]],
        output_core_dims=[["parameter1"]],
        output_sizes={"parameter1": 5},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
    )

    fitted= fitted.assign_coords(parameter1=["a", "loc", "scale","KS-fit","p-value"])
    fitted.name = "gamma_params"
    return fitted
    
# Wrap into apply_ufunc
def fit_lognorm(a):
    fitted = apply_ufunc(
        _fit_lognorm_1d,
        a,
        input_core_dims=[["time"]],
        output_core_dims=[["parameter1"]],
        output_sizes={"parameter1": 5},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
    )
    
    fitted= fitted.assign_coords(parameter1=["a", "loc", "scale","KS-fit","p-value"])
    fitted.name = "lognorm_params"
    return fitted

# Wrap into apply_ufunc
def fit_invgauss(a):
    fitted = apply_ufunc(
        _fit_invgauss_1d,
        a,
        input_core_dims=[["time"]],
        output_core_dims=[["parameter1"]],
        output_sizes={"parameter1": 5},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
    )
    
    fitted= fitted.assign_coords(parameter1=["a", "loc", "scale","KS-fit","p-value"])
    fitted.name = "invgauss_params"
    return fitted




####### Sobol routines

def _ffdi(x):
#ffdi = drought_factor**0.987 * np.exp(0.0338 * tasmax - 0.0345 * hurs 
#      + 0.0234 * sfcWind + 0.243147)
# Tmax/29.5 - rhum/29 + wind/42.7
    f_eval = (
        x[0]**0.987 * np.exp(0.0338 * x[1] - 0.0345 * x[2] 
        + 0.0234 * x[3]*3.6  + 0.243147)
    )
    return f_eval
    
def sobol_indices_1d(fit1,fit2,fit3,fit0):
    rng = np.random.default_rng()
    indices = sobol_indices(
        func=_ffdi, n=1024,
        dists=[
        gamma(a=fit0[0],loc=fit0[1],scale=fit0[2]),
        gamma(a=fit1[0],loc=fit1[1],scale=fit1[2]),
        gamma(a=fit2[0],loc=fit2[1],scale=fit2[2]),
        gamma(a=fit3[0],loc=fit3[1],scale=fit3[2]),
        ],
        random_state=rng, )
    return np.array([indices.first_order]), np.array([indices.total_order])

# dists=[
#        gamma(a=276.56, loc=-10.67, scale=0.07),
#        beta(a=4.51,b=4.64, loc=23.6,scale=24.2),
#        beta(a=3.64,b=8.83,loc=4.76,scale=37.99),
#        beta(a=6.28,b=7.46,loc=1.55,scale=13.97)
#    ],

def xr_sobol_indices(fit1,fit2,fit3,fit0):
    results1,results2 = apply_ufunc(
        sobol_indices_1d,
        fit1,fit2,fit3,fit0,
        input_core_dims=[["parameter1"],["parameter1"],["parameter1"],["parameter1"]],
        output_core_dims=[["sa_1"],["sa_1"]],
        output_sizes={"sa_1": 4, "sa_1":4 },
        vectorize=True,            # allow broadcasting over lat/lon
        dask="parallelized",       # enable Dask
        output_dtypes=[float,float],
    )
    results1= results1.assign_coords(sa_1=["DI", "Tmax", "Hmin", "Wmax"])
    results1.name = "sobol_indices_1st"
    results2= results2.assign_coords(sa_1=["DI", "Tmax", "Hmin", "Wmax"])
    results2.name = "sobol_indices_tot"
    return results1,results2
#        input_core_dims=[["time"],[],[]],
#        join="override",

def sobol_indices_1du(fit1):
    rng = np.random.default_rng()
    indices = sobol_indices(
        func=_ffdi, n=1024,
        dists=[
        uniform(loc=5, scale=5),
        uniform(loc=24, scale=19),
        uniform(loc=0, scale=30),
        uniform(loc=3, scale=10)
        ],
        random_state=rng, )

# New version that remove min and directly computes samples
def xr_sobol_indices_v2(fit1,fit2,fit3,fit4,arr1,arr2,arr3,arr4,n_samples):
    results = apply_ufunc(
        _sobol_indices_calc_1d,
        fit1,fit2,fit3,fit4,arr1,arr2,arr3,arr4,n_samples,
        input_core_dims=[["parameter1"],["parameter1"],["parameter1"],["parameter1"],[],[],[],[],[]],
        output_core_dims=[["stat", "sa_1"]],
        output_sizes={"stat": 2, "sa_1": 4},
        vectorize=True,            # allow broadcasting over lat/lon
        dask="parallelized",       # enable Dask
        output_dtypes=[float],
    )
    results= results.assign_coords(sa_1=["DI", "Tmax", "Hmin", "Wmax"])
    results.name = "sobol_indices"
#    results2= results2.assign_coords(sa_1=["DI", "Tmax", "Hmin", "Wmax"])
#    results2.name = "sobol_indices_tot"
#    return results1,results2
    return results

def _sobol_indices_calc_1d(fit1,fit2,fit3,fit4, a,b,c,d, n_samples):
    """
    Generates Sobol indices from samples transformed to match specified 
    distributions over [0, ∞) provided by the fit terms.
    Parameters:
        distributions (list of scipy.stats.rv_continuous): 
            List of distributions (must support .ppf) with support on [0, ∞)
        Amin (array of minimum values to add to samples
        n_samples (int): 
            Number of samples to generate for A, B
    Returns:
        np.ndarray: Transformed Sobol samples of shape (n_samples, n_variables)
        array of the calculated sobol indices
    """
    func=_ffdi    
    Amin=[a,b,c,d]
    distributions = [
        gamma(a=fit1[0], loc=fit1[1], scale=fit1[2]),
        gamma(a=fit2[0], loc=fit2[1], scale=fit2[2]),
        gamma(a=fit3[0], loc=fit3[1], scale=fit3[2]),
        gamma(a=fit4[0], loc=fit4[1], scale=fit4[2]),
        ]
    d = len(distributions)
# Create random uniform sample from 0 to 1 (n_samples x d)
    rng = np.random.default_rng(seed=0)
    A_u = rng.uniform(0, 1, size=(n_samples, d))
    B_u = rng.uniform(0, 1, size=(n_samples, d))
# Quick independence check: correlations of columns should be ~0
#    for i in range(d):
#        corr = np.corrcoef(A_u[:, i], B_u[:, i])[0, 1]
#        print(f"corr A[:,{i}] vs B[:,{i}] = {corr:.6f}")
# Transform using inverse CDF (PPF) of each distribution
    A = np.column_stack([ dist.ppf(A_u[:, i])
        for i, dist in enumerate(distributions) ])
    B = np.column_stack([ dist.ppf(B_u[:, i])
        for i, dist in enumerate(distributions) ])
# Add min offset to A and B
#    print(np.min(A,axis=0))
    A=A+Amin
    B=B+Amin
#    print(np.min(A,axis=0))
# Create hybrid matrices A_B[i]
    AB = np.zeros((d, n_samples, d))
    for i in range(d):
        AB[i] = A.copy()
        AB[i][:, i] = B[:, i]
# Evaluate on A, B, and each AB_i
    f_A = func(A.T)                  # shape (N,)
    f_B = func(B.T)                  # shape (N,)
    f_AB = np.array([_ffdi(AB[i].T) for i in range(d)])
# Compute Sobol indices manually (Jansen estimator)
    V = np.var(np.concatenate([f_A, f_B]), ddof=0)
    S1 = np.array([np.mean(f_B * (f_AB[i] - f_A)) / V for i in range(d)])
    ST = np.array([0.5 * np.mean((f_A - f_AB[i])**2) / V for i in range(d)])
# Clip to [0,1] and round 
    S1 = np.round(np.clip(S1, 0, 1),4)
    ST = np.round(np.clip(ST, 0, 1),4)
    
#    return f_A,f_B,f_AB,S1,ST
#    return S1,ST
    return np.stack([S1, ST], axis=0)  # shape (2, d)
    

########  Permutation sensitivity #####################
import xarray as xr
from xarray import apply_ufunc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.inspection import permutation_importance

def _perm_importance_1d(Dmax,Tmax,Hmin,Wmax,FFDI):
    b1 = FFDI
    a1 = Dmax
    a2 = Tmax
    a3 = Hmin
    a4 = Wmax

    y=(b1[~np.isnan(a1)])  # use a1 because it can be smallest
    if len(y) < 5:
        return np.stack([np.full(4, np.nan), np.full(4, np.nan), np.full(4, np.nan)],
                    axis=0)
    try:
        x1=a1[~np.isnan(a1)]
        x2=a2[~np.isnan(a1)]
        x3=a3[~np.isnan(a1)]
        x4=a4[~np.isnan(a1)]
        X=np.stack((x1,x2,x3,x4),axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, 
                        test_size=0.2, random_state=0)
# Train a Random Forest
        model = RandomForestRegressor(n_estimators=200, random_state=0,)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_tpred = model.predict(X_train)
# Metrics
        r2 = r2_score(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        rmset = mean_squared_error(y_train, y_tpred, squared=False)
        mae = mean_absolute_error(y_test, y_pred)
# Compute importance on data
        result = permutation_importance(model, X_test, y_test,
                    n_repeats=10, random_state=42)
#        return result.importances_mean,result.importances_std, np.array([r2,rmse,rmset])
        return np.stack([result.importances_mean,result.importances_std,
            np.array([r2,rmse,rmset,mae])],axis=0)   
#        return np.array([result.importances_mean, 
#                result.importances_std, r2,rmse,rmset])2
    except Exception:
        return np.stack([np.full(4, np.nan), np.full(4, np.nan), np.full(4, np.nan)],
            axis=0)
#        return np.full(4, np.nan), np.full(4, np.nan), np.full(3, np.nan)
        
# Compute importance on data    
def xr_perm_importance(Dmax,Tmax,Hmin,Wmax,FFDI):
    r1= apply_ufunc(
        _perm_importance_1d,
        Dmax,Tmax,Hmin,Wmax,FFDI,
        input_core_dims=[["time"],["time"],["time"],["time"],["time"]],
        output_core_dims=[["stat", "nvar"]],
        output_sizes={"stat": 3, "nvar": 4},
        vectorize=True,            # allow broadcasting over lat/lon
        dask="parallelized",       # enable Dask
        output_dtypes=[float],
    )
    names1=["DI","Tmax","Hmin","Wmax"]
    names2=["mean","std","diag"]
    diags=["r2", "rmse","rmse_t","mae"]
    r1= r1.assign_coords(nvar=names1,stat=names2)
    r1.name = "permutation_importance"
    return r1
