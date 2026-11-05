import RuleOfX.Frontier
import RuleOfX.Score
import RuleOfX.Saturation
import RuleOfX.Envelope
import RuleOfX.Capital
import RuleOfX.Budget
import RuleOfX.BudgetCont

/-!
# Axiom check

`#print axioms` for every main theorem. The expected output for each is
`[propext, Classical.choice, Quot.sound]` and nothing else (in particular no `sorryAx`).
-/

namespace RuleOfX

#print axioms one_lt_β
#print axioms Cα_pos
#print axioms Cα_lt_one
#print axioms prop_frontier_a
#print axioms prop_frontier_b
#print axioms prop_frontier_c
#print axioms prop_frontier_d
#print axioms prop_score_a
#print axioms prop_score_b
#print axioms prop_score_c
#print axioms prop_score_d
#print axioms prop_score_d_uncapped
#print axioms prop_score_e
#print axioms prop_saturation_a
#print axioms prop_saturation_b
#print axioms prop_saturation_c
#print axioms prop_saturation_d
#print axioms prop_envelope
#print axioms cor_capital
#print axioms cor_priorities_i
#print axioms cor_priorities_ii
#print axioms cor_priorities_iii
#print axioms cor_priorities_v
#print axioms prop_budget_b
#print axioms prop_budget_c_discrete
#print axioms cor_transient_a
#print axioms prop_budget_a
#print axioms prop_budget_c_continuous
#print axioms cor_transient_b
#print axioms cor_transient_b_optimum
#print axioms induced_isPath
#print axioms prop_budget_a_induced
#print axioms prop_budget_c_continuous_induced
#print axioms cor_transient_b_induced
#print axioms cor_transient_b_optimum_induced

end RuleOfX
