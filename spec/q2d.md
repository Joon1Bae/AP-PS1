The linear model to be estimated is as follows:

xR_{e,t+1} = a + b·Dt/Pt + ε_t

where xR_{e,t+1} is the 12-month excess return realized at t+12 months and D_t/P_t is the dividend–price ratio observed at t.

for each t (t starts from December 1940 for xR_{e, t+1} and Dec 1939 for Dt/Pt.)
estimate a^ and b^(in this case, two estimated coefficents are time-varing)

for each t, the observed data spans from the start point(maybe 1927?) to the information available until time t.


Details are in the below.

Item 1. At each time t, You can only access to the information available until time t.
For example, t = Dec 1939, you can estimate the coefficient until xR_e,t+1 is available until Dec 1939.
Therefore, the regression at t uses pairs (D_s/P_s, xR_{e,s+1}) whose return is realized by t, i.e., s ≤ t − 12 months, giving time-varying â_t, b̂_t


Item 2. 

R2_OS = 1− ∑(xR_{e,t+1} - E^hat_t[xR_{e, t+1}])^2/∑(xR_{e,t+1} - xR^bar_e,t)^2

where E^hat_t[xR_{e,t+1}] = a^hat_t + b^hat_t·D_t/P_t. 

Item 3. You should use the same cutoff as the regression when you calculate the historical average xR_e,t^barall 12-month excess returns realized by t, including the return realized at 1927:12 (which has no D/P twelve months earlier and never enters the regression).

Item 4. In-sample fitted line is the fitted value, i.e.,
E^hat_t[xRe] = a^hat + b^hat D_t*P_t where a^hat and b^hat are estimated with the full sample (predictor dates 1927:12–2020:12)

Item 5. please calculate ROS using a 50-year rolloing window.
a^hat_t, b^hat_t and xR^bar_{e,t} does not change.
only the two sums in R²_OS run over the window.
Windows are 600 consecutive forecast-target months ending at T, for T = 1990:12, 1991:01, …, end of sample (first window 1941:01–1990:12).
