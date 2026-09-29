Estimate the following regression model:

(1/4)Σ_{H=2}^5 xr^(H)_{t+12} = \theta_0 + \Sigma^5_{H=1} (\theta_h) * f^(H)_{b, t} + u_t

cp_t is defined as a fitted value only on regression dates.

t-statistics should be calculated based on Newey and West (1994), but you don't have to report it, because what we want is to plot the estimated value.

Regarding NBER shading you can refer to the data/USREC.csv file.

Output should be a figure of cp_t with gray recession bands.