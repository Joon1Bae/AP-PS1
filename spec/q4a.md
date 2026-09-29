Data: data/bond.csv

Please only keep TTERMLBL = "Fama Bliss Discount Bonds - X-Year (Nominal)", X=1..5
TMYTM = yield in percent
date = MCALDT
period: full sample from  1952-06-30 to 2024-12-31.

And please calculate each variables as follows:

y^(H) = log(1 + TMYTM/100)
f^(H) = H y^(H) − (H−1) y^(H−1), f^(1) = y^(1)
r^(H)_t = H y^(H)_{t−12} − (H−1) y^(H−1)_t, r^(1)_t = y^(1)_{t−12}


xy, xf, xr = each minus its H=1 counterpart.

What I mean by "full sample" is that the common sample on which xy, xf and xr are all defined

Output should be the table of means for H=2..5 in %.