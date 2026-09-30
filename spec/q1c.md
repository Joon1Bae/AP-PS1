VAR
- z_t = [Δd_t, r_{e,t}, dp_t]' as in the Problem.

Estimate the following regression model:

z_{t+1} = Γ_0 + Γ * z_t + \tilde z_t+1 where \tilde z_t+1 follows IID(0, \Sigma)

OLS equation by equation, on all months with z_{t+1} in the data. 

Implied terms (same k = 0.9642 and H = 1, …, 15 as q1b):
  b_re^(H) =  \Sigma_{h=1}^H κ^{h−1} e_r' Γ^h \Sigma_z e_dp / Var[dp]
  b_\delta d^(H) = −\Sigma_{h=1}^H κ^{h−1} e_Δd' Γ^h \Sigma_z e_dp / Var[dp]
  b_dp^(H) =  κ^H e_dp' Γ^H \Sigma_z e_dp / Var[dp]
You should report their sum for each H as in q1b.

Output should be figure analogous to q1b (same style; same y-axis range as q1b if the values fit) and table of b_re, b_Δd, b_dp, their sum, by H, as in q1b.

.tex (Section 1.3): Task block quoted verbatim above the results. Then state the following derivation briefly, conclusions only, no step-by-step proof:
- With μ = (I − Γ)^{-1} Γ0, iterating (1.5) forward h times gives
  z_{t+h} − μ = Γ^h (z_t − μ) + Σ_{j=1}^h Γ^{h−j} z̃_{t+j},
  so E_t[z_{t+h}] − μ = Γ^h (z_t − μ).
- Since future shocks are uncorrelated with z_t, Cov[z_{t+h}, dp_t] = Γ^h Σ_z e_dp,
  where Σ_z solves Σ_z = Γ Σ_z Γ' + Σ.
- Substituting into Equation 1.4 gives the three expressions above.

Keep this to a few lines of display math with one short sentence each.


Your questions have been answered: 
- "What is one period in the VAR? The data are monthly observations of annual variables, and in Q1b one step h is 12 months. The spec says 'all months with z_{t+1} in the data' but not how far ahead t+1 is."="12 months, as in Q1b"
- "Which Var[dp] goes in the denominator of the three terms?"="VAR-implied". You can now continue with these answers in mind.