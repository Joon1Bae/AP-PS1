The linear model to be estimated is as follows:

xR_{e,t+1} = a + b·Dt/Pt + ε_t

for each t (t starts from December 1940 for xR_{e, t+1} and Dec 1939 for Dt/Pt.)
estimate a^ and b^(in this case, two estimated coefficents are time-varing)

for each t, the observed data spans from the start point(maybe 1927?) to the information available until time t.


Details are in the below.

Item 1. At each time t, You can only access to the information available until time t.
For example, t = Dec 1939, 
you can estimate the coefficient until 
xR_e,t+1 is available until Dec 1939.

Item 2. 
R2_OS = 1− ∑(xr_e,t+1 - E_t[x+re])^2/∑(xr_e,t+1 - xr^bar_e,t)^2


Item 3. You should use the same cutoff as the regression when you calculate the historical average xR_e,t^bar.

Item 4. In-sample fitted line is the fitted value, i.e.,
E^hat_t[xRe] = a^hat + b^hat D_t*P_t where a^hat and b^hat are estimated with the full sample.

Item 5. please calculate ROS using a 50-year rolloing window.
