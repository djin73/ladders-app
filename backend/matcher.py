from ortools.sat.python import cp_model
from typing import List, Set, Tuple


class LaddersMatcher:
    N_PENALTIES = 4
    N_CG = 6
    SCHEDULING_OPTIONS = ["Breakfast", "Morning", "Lunch", "Afternoon", "Dinner"]

    def __init__(self, people_dir, prev_dir):
        """Initialize the matcher, using the preferences stored at people_dir."""
        self.outdir = prev_dir
        self.people_info: List[List] = []
        with open(people_dir, "r") as file:
            for line in file.read().splitlines():
                self.people_info.append(line.split("; "))
            file.close()

        # NOTE: we are only performing matches for an even number of people
        if len(self.people_info) % 2 == 1:
            self.people_info.pop()
        self.n_people = len(self.people_info)
        self.names: List[str] = [self.people_info[i][0] for i in range(self.n_people)]

        # gender[x] = gender of person x; 0 = male, 1 = female
        self.gender: List[int] = [
            int(self.people_info[i][2]) for i in range(self.n_people)
        ]
        # gender[x] = gender of person x; -1 = neither, 0 = male, 1 = female
        self.gender_pref: List[int] = [
            int(self.people_info[i][6]) for i in range(self.n_people)
        ]

        # year[x] = year of person x; 1 = freshman, 2 = sophomore, 3 = junior, 4 = senior+
        self.year: List[int] = [
            int(self.people_info[i][3]) for i in range(self.n_people)
        ]

        # year_pref[x] = preferred year(s) to be matched to
        self.year_pref: List[Set[int]] = [
            set(eval(self.people_info[i][7])) for i in range(self.n_people)
        ]

        # cg_of[x] = the participant's CG
        self.cg_of: List[int] = [
            int(self.people_info[i][5]) for i in range(self.n_people)
        ]

        # list of all previous pairings
        self.prev_pairings: List[List[Tuple[str]]] = []
        with open(prev_dir, "r") as file:
            for line in file.read().splitlines():
                self.prev_pairings.append(eval(line))
            file.close()

        self.pref_not_partners: List[Set[int]] = [
            set(eval(self.people_info[i][8])) for i in range(self.n_people)
        ]

        self.scheduling_pref: List[Set[int]] = [
            set(eval(self.people_info[i][9])) for i in range(self.n_people)
        ]

    def create_variables(self):
        """Create and store the variables for the model."""
        n_people = self.n_people
        model: cp_model.CpModel = self.model
        names = self.names
        # partner_of[x] = index of person x's partner
        self.partner_of: List[cp_model.IntVar] = [
            model.NewIntVar(0, n_people - 1, f"partner of {names[i]}({i})")
            for i in range(n_people)
        ]

        # regenerate list of previous partners using (potentially updated) self.prev_pairings
        # prev_partners[x] = list of people that x has been paired with previously (most recent first?)
        self.prev_partners: List[List[int]] = [[] for _ in range(self.n_people)]
        self.name_to_id = {name: i for i, name in enumerate(self.names)}
        for list_of_pairs in self.prev_pairings:
            for name1, name2 in list_of_pairs:
                self.prev_partners[self.name_to_id[name1]].append(
                    self.name_to_id[name2]
                )
                self.prev_partners[self.name_to_id[name2]].append(
                    self.name_to_id[name1]
                )

    def create_hard_constraints(self):
        """Adds hard constraints to the model: 1 to 1 pairing, different CGs, new pairings."""
        model: cp_model.CpModel = self.model
        n_people = self.n_people
        partner_of = self.partner_of
        names = self.names
        cg_of = self.cg_of
        prev_partners = self.prev_partners

        # 1 to 1 pairing
        model.AddInverse(partner_of, partner_of)
        for i in range(n_people):
            model.Add(partner_of[i] != i)

        # constraint for different CGs
        self.cg_of_partner_of = [
            model.NewIntVar(1, LaddersMatcher.N_CG, f"CG of partner of {names[i]}({i})")
            for i in range(n_people)
        ]
        for i in range(n_people):
            # cg_of_partner_of[i] == cg_of[partner_of[i]]
            model.AddElement(partner_of[i], cg_of, self.cg_of_partner_of[i])
            model.Add(self.cg_of_partner_of[i] != cg_of[i])

        # constraint for new pairings
        for i, old_partners in enumerate(prev_partners):
            for old_partner in old_partners:
                model.Add(partner_of[i] != old_partner)

    def create_soft_constraints(self):
        """Adds soft constraints: gender preferences, year preferences, scheduling preferences, pairing preferences."""
        model: cp_model.CpModel = self.model
        n_people = self.n_people
        partner_of = self.partner_of
        names = self.names

        # gender preferences and penalty
        self.gender_pref_violated: List[cp_model.IntVar] = [
            model.NewBoolVar(f"gender preference of {names[i]}({i}) violated")
            for i in range(n_people)
        ]
        self.gender_of_partner_of: List[cp_model.IntVar] = [
            model.NewIntVar(0, 1, f"gender of partner of {names[i]}({i})")
            for i in range(n_people)
        ]
        for i in range(n_people):
            if self.gender_pref[i] != -1:
                model.AddElement(
                    partner_of[i], self.gender, self.gender_of_partner_of[i]
                )
                model.Add(
                    self.gender_of_partner_of[i] == self.gender_pref[i]
                ).OnlyEnforceIf(self.gender_pref_violated[i].Not())
                # in general, only need one of the reification constraints because we're minimizing violations
            else:
                model.Add(self.gender_pref_violated[i] == 0)
        self.gender_penalty = model.NewIntVar(0, n_people, "gender penalty")
        model.Add(self.gender_penalty == sum(self.gender_pref_violated))

        # year preferences and penalty
        self.year_pref_violated: List[cp_model.IntVar] = [
            model.NewBoolVar(f"year preference of {names[i]}({i}) violated")
            for i in range(n_people)
        ]
        self.year_of_partner_of: List[cp_model.IntVar] = [
            model.NewIntVar(1, 4, f"year of partner of {names[i]}({i})")
            for i in range(n_people)
        ]

        for i in range(n_people):
            model.AddElement(partner_of[i], self.year, self.year_of_partner_of[i])
            model.AddLinearExpressionInDomain(
                self.year_of_partner_of[i],
                cp_model.Domain.FromValues(list(self.year_pref[i])),
            ).OnlyEnforceIf(self.year_pref_violated[i].Not())
        self.year_penalty = model.NewIntVar(0, n_people, "year penalty")
        model.Add(self.year_penalty == sum(self.year_pref_violated))

        # scheduling preferences and penalty
        self.scheduling_pref_violated: List[cp_model.IntVar] = [
            model.NewBoolVar(f"scheduling preference of {names[i]}({i}) violated")
            for i in range(n_people)
        ]
        for a in range(n_people):
            for b in range(a + 1, n_people):
                # intersection is empty set
                if not self.scheduling_pref[a].intersection(self.scheduling_pref[b]):
                    model.Add(partner_of[a] != b).OnlyEnforceIf(
                        self.scheduling_pref_violated[a].Not()
                    )  # no violation => not matched
                    model.Add(partner_of[b] != a).OnlyEnforceIf(
                        self.scheduling_pref_violated[b].Not()
                    )
        self.scheduling_penalty = model.NewIntVar(0, n_people, "scheduling penalty")
        model.Add(self.scheduling_penalty == sum(self.scheduling_pref_violated))

        # pairing preferences and penalty
        self.pairing_pref_violated: List[cp_model.IntVar] = [
            model.NewBoolVar(f"partner preferences of {names[i]}({i}) violated")
            for i in range(n_people)
        ]
        for i in range(n_people):
            model.AddLinearExpressionInDomain(
                partner_of[i],
                cp_model.Domain.FromValues(
                    list(set(range(n_people)) - self.pref_not_partners[i])
                ),
            ).OnlyEnforceIf(self.pairing_pref_violated[i].Not())
        self.pairing_penalty = model.NewIntVar(0, n_people, "pairing penalty")
        model.Add(self.pairing_penalty == sum(self.pairing_pref_violated))

        self.total_penalty = model.NewIntVar(
            0, LaddersMatcher.N_PENALTIES * n_people, f"total penalty"
        )
        model.Add(
            self.total_penalty
            == self.gender_penalty
            + self.year_penalty
            + self.scheduling_penalty
            + self.pairing_penalty
        )

    def solve(self):
        """Initializes the solver and solves the problem, creating the matching."""
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.create_variables()
        self.create_hard_constraints()
        self.create_soft_constraints()

        self.model.Minimize(self.total_penalty)
        result = self.solver.Solve(self.model)
        if result == cp_model.OPTIMAL or result == cp_model.FEASIBLE:
            self.final_pairings = [
                (self.names[i], self.names[self.solver.Value(self.partner_of[i])])
                for i in range(self.n_people)
                if i < self.solver.Value(self.partner_of[i])
            ]
            self.final_penalties = {
                "gender": [
                    i
                    for i in range(self.n_people)
                    if self.solver.Value(self.gender_pref_violated[i])
                ],
                "year": [
                    i
                    for i in range(self.n_people)
                    if self.solver.Value(self.year_pref_violated[i])
                ],
                "scheduling": [
                    i
                    for i in range(self.n_people)
                    if self.solver.Value(self.scheduling_pref_violated[i])
                ],
                "pairing": [
                    i
                    for i in range(self.n_people)
                    if self.solver.Value(self.pairing_pref_violated[i])
                ],
            }
            self.print_pairings()
            self.print_penalties()
        else:
            raise ValueError("Not possible!")

    def print_pairings(self):
        print("FINAL PARTNERS:", self.final_pairings)

    def print_penalties(self):
        print("TOTAL PENALTY:", self.solver.Value(self.total_penalty))
        print("Preference violations:")
        for violation_bool in (
            self.gender_pref_violated
            + self.year_pref_violated
            + self.scheduling_pref_violated
            + self.pairing_pref_violated
        ):
            if self.solver.Value(violation_bool):
                print("-", violation_bool.Name())

    def save_match_to_object(self):
        """Saves the matches to the current matcher object."""
        try:
            final_pairings = self.final_pairings
            self.prev_pairings.append(final_pairings)
        except AttributeError:
            print("Failed to save matches to object: solver has no current solution!")

    def save_match_to_txt(self):
        """Saves the matches to the specified output file."""
        final_pairings = self.final_pairings
        with open(self.outdir, "a") as file:
            file.write(f"{final_pairings}\n")
            file.close()
        print(f"Succesfully saved pairing to {self.outdir}!")
