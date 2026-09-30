Compute the following equation using Γ, Σ_z, κ from q1c:

- b_re^(\inf) = e_r'Γ(I−κΓ)^{-1}Σ_z e_dp / Var[dp] 
- b_\delta d^(\int) = −e_Δd'Γ(I−κΓ)^{-1}Σ_z e_dp / Var[dp] 

This uses Σ_{h≥1} κ^{h−1} Γ^h = Γ (I − κΓ)^{-1}, which holds when all eigenvalues of κΓ are inside the unit circle. So, please check max |eig(κΓ)| < 1 and report it.

Output should be the two numbers and their sum as macros.

Regarding interpretation, please leave it as blank. I will write it down by myself.