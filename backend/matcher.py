from ortools.sat.python import cp_model
from typing import List, Set


class LaddersMatcher:
    N_PENALTIES = 4
    N_CG = 6
    SCHEDULING_OPTIONS = ['Breakfast', 'Morning',
                          'Lunch', 'Afternoon', 'Dinner']

    def __init__(self, people_dir, prev_dir):
        '''Initialize the matcher, using the preferences stored at people_dir.'''
        # TODO: explicitly take the first (even) number
        self.people_info: List[List] = []
        with open(people_dir, 'r') as file:
            for line in file.read().splitlines():
                self.people_info.append(line.split("; "))
            file.close()

        self.n_people = len(self.people_info)
        self.names: List[str] = [self.people_info[i][0]
                                 for i in range(self.n_people)]

        # gender[x] = gender of person x; 0 = male, 1 = female
        self.gender: List[int] = [int(self.people_info[i][1])
                                  for i in range(self.n_people)]
        # gender[x] = gender of person x; -1 = neither, 0 = male, 1 = female
        self.gender_pref: List[int] = [int(self.people_info[i][5])
                                       for i in range(self.n_people)]

        # year[x] = year of person x; 1 = freshman, 2 = sophomore, 3 = junior, 4 = senior+
        self.year: List[int] = [int(self.people_info[i][2])
                                for i in range(self.n_people)]

        # year_pref[x] = preferred year(s) to be matched to
        self.year_pref: List[Set[int]] = [set(eval(self.people_info[i][6]))
                                          for i in range(self.n_people)]

        # cg_of[x] = the participant's CG
        self.cg_of: List[int] = [int(self.people_info[i][4])
                                 for i in range(self.n_people)]

        # prev_partners[x] = list of people that x has been paired with previously (most recent first?)
        self.name_to_id = {name: i for i, name in enumerate(self.names)}
        self.prev_partners: List[List[int]] = [[]
                                               for _ in range(self.n_people)]
        with open(prev_dir, 'r') as file:
            for line in file.read().splitlines():
                pairings = eval(line)
                for name1, name2 in pairings:
                    self.prev_partners[self.name_to_id[name1]].append(
                        self.name_to_id[name2])
                    self.prev_partners[self.name_to_id[name2]].append(
                        self.name_to_id[name1])
            file.close()

        self.pref_not_partners: List[Set[int]] = [
            set(eval(self.people_info[i][7])) for i in range(self.n_people)]

        self.scheduling_pref: List[Set[int]] = [
            set(eval(self.people_info[i][8])) for i in range(self.n_people)]

    def create_variables(self):
        '''Create and store the variables for the model.'''
        n_people = self.n_people
        model: cp_model.CpModel = self.model
        names = self.names
        # partner_of[x] = index of person x's partner
        self.partner_of: List[cp_model.IntVar] = [model.NewIntVar(
            0, n_people - 1, f'partner of {names[i]}({i})') for i in range(n_people)]

    def create_hard_constraints(self):
        '''Adds hard constraints to the model: 1 to 1 pairing, different CGs, new pairings.'''
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
        self.cg_of_partner_of = [model.NewIntVar(
            1, LaddersMatcher.N_CG, f'CG of partner of {names[i]}({i})') for i in range(n_people)]
        for i in range(n_people):
            # cg_of_partner_of[i] == cg_of[partner_of[i]]
            model.AddElement(partner_of[i], cg_of, self.cg_of_partner_of[i])
            model.Add(self.cg_of_partner_of[i] != cg_of[i])

        # constraint for new pairings
        # TODO is there a more efficient way to do this?
        for i, old_partners in enumerate(prev_partners):
            for old_partner in old_partners:
                model.Add(partner_of[i] != old_partner)

    def create_soft_constraints(self):
        '''Adds soft constraints: gender preferences, year preferences, scheduling preferences, pairing preferences.'''
        model: cp_model.CpModel = self.model
        n_people = self.n_people
        partner_of = self.partner_of
        names = self.names

        # gender preferences and penalty
        self.gender_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
            f'gender preference of {names[i]}({i}) violated') for i in range(n_people)]
        self.gender_of_partner_of: List[cp_model.IntVar] = [model.NewIntVar(
            0, 1, f'gender of partner of {names[i]}({i})') for i in range(n_people)]
        for i in range(n_people):
            if self.gender_pref[i] != -1:
                model.AddElement(
                    partner_of[i], self.gender, self.gender_of_partner_of[i])
                model.Add(self.gender_of_partner_of[i] == self.gender_pref[i]).OnlyEnforceIf(
                    self.gender_pref_violated[i].Not())
                # in general, only need one of the reification constraints because we're minimizing violations
            else:
                model.Add(self.gender_pref_violated[i] == 0)
        self.gender_penalty = model.NewIntVar(0, n_people, 'gender penalty')
        model.Add(self.gender_penalty == sum(self.gender_pref_violated))

        # year preferences and penalty
        self.year_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
            f'year preference of {names[i]}({i}) violated') for i in range(n_people)]
        self.year_of_partner_of: List[cp_model.IntVar] = [model.NewIntVar(
            1, 4, f'year of partner of {names[i]}({i})') for i in range(n_people)]

        for i in range(n_people):
            model.AddElement(partner_of[i], self.year,
                             self.year_of_partner_of[i])
            model.AddLinearExpressionInDomain(self.year_of_partner_of[i], cp_model.Domain.FromValues(
                self.year_pref[i])).OnlyEnforceIf(self.year_pref_violated[i].Not())
        self.year_penalty = model.NewIntVar(0, n_people, 'year penalty')
        model.Add(self.year_penalty == sum(self.year_pref_violated))

        # scheduling preferences and penalty
        self.scheduling_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
            f'scheduling preference of {names[i]}({i}) violated') for i in range(n_people)]
        for a in range(n_people):
            for b in range(a+1, n_people):
                # intersection is empty set
                if not self.scheduling_pref[a].intersection(self.scheduling_pref[b]):
                    model.Add(partner_of[a] != b).OnlyEnforceIf(
                        self.scheduling_pref_violated[a].Not())  # no violation => not matched
                    model.Add(partner_of[b] != a).OnlyEnforceIf(
                        self.scheduling_pref_violated[b].Not())
        self.scheduling_penalty = model.NewIntVar(
            0, n_people, 'scheduling penalty')
        model.Add(self.scheduling_penalty == sum(
            self.scheduling_pref_violated))

        # pairing preferences and penalty
        self.pairing_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
            f'partner preferences of {names[i]}({i}) violated') for i in range(n_people)]
        for i in range(n_people):  # TODO is this inefficient? not sure
            model.AddLinearExpressionInDomain(partner_of[i], cp_model.Domain.FromValues(set(
                range(n_people)) - self.pref_not_partners[i])).OnlyEnforceIf(self.pairing_pref_violated[i].Not())
        self.pairing_penalty = model.NewIntVar(0, n_people, 'pairing penalty')
        model.Add(self.pairing_penalty == sum(self.pairing_pref_violated))

        self.total_penalty = model.NewIntVar(
            0, LaddersMatcher.N_PENALTIES * n_people, f'total penalty')
        model.Add(self.total_penalty == self.gender_penalty + self.year_penalty +
                  self.scheduling_penalty + self.pairing_penalty)

    def solve(self):
        '''Initializes the solver and solves the problem, creating the matching.'''
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.create_variables()
        self.create_hard_constraints()
        self.create_soft_constraints()

        self.model.Minimize(self.total_penalty)
        result = self.solver.Solve(self.model)
        if result == cp_model.OPTIMAL or result == cp_model.FEASIBLE:
            self.final_pairings = [(self.names[i], self.names[self.solver.Value(self.partner_of[i])])
                                   for i in range(self.n_people) if i < self.solver.Value(self.partner_of[i])]
            self.print_pairings()
            self.print_penalties()
        else:
            raise ValueError('Not possible!')

    def print_pairings(self):
        print('FINAL PARTNERS:', self.final_pairings)

    def print_penalties(self):
        print('TOTAL PENALTY:', self.solver.Value(self.total_penalty))
        print('Preference violations:')
        for violation_bool in self.gender_pref_violated + self.year_pref_violated + self.scheduling_pref_violated + self.pairing_pref_violated:
            if self.solver.Value(violation_bool):
                print('-', violation_bool.Name())

    def save_match(self, outdir):
        '''Saves the matches to the specified output file.'''
        try:
            final_pairings = self.final_pairings
            with open(outdir, 'a') as file:
                file.write(f'{final_pairings}\n')
                file.close()
            print(f'Succesfully saved pairing to {outdir}!')
        except AttributeError:
            print('Failed to save matches: solver has no current solution!')


# matcher = LaddersMatcher("people.txt", "previous-matches.txt")
# matcher.solve()
# matcher.save_match("previous-matches.txt")


'''
## ----- INPUTS ----- ##

people_info: List[List] = []
with open('people.txt', 'r') as file:
    for line in file.read().splitlines():
        people_info.append(line.split("; "))

n_people = len(people_info)
names: List[str] = [people_info[i][0] for i in range(n_people)]

# gender[x] = gender of person x; 0 = male, 1 = female
gender: List[int] = [int(people_info[i][1]) for i in range(n_people)]
# gender[x] = gender of person x; -1 = neither, 0 = male, 1 = female
gender_pref: List[int] = [int(people_info[i][5]) for i in range(n_people)]

# year[x] = year of person x; 1 = freshman, 2 = sophomore, 3 = junior, 4 = senior+
year: List[int] = [int(people_info[i][2]) for i in range(n_people)]
POSSIBLE_YEARS = {1, 2, 3, 4}

# year_pref[x] = preferred year(s) to be matched to
year_pref: List[Set[int]] = [set(eval(people_info[i][6]))
                             for i in range(n_people)]

# cg_of[x] = the participant's CG
cg_of: List[int] = [int(people_info[i][4]) for i in range(n_people)]

# prev_partners[x] = list of people that x has been paired with previously (most recent first?)
prev_partners: List[List[int]] = []

pref_not_partners: List[Set[int]] = [
    set(eval(people_info[i][7])) for i in range(n_people)]

# TODO scheduling
SCHEDULING_OPTIONS = ['Breakfast', 'Morning', 'Lunch', 'Afternoon', 'Dinner']
scheduling_pref: List[Set[int]] = [
    set(eval(people_info[i][8])) for i in range(n_people)]

# TODO: Don't forget to account number of people eventually (odd)
# TODO: incoroporate stuff like major/school into profile
# TODO: worry about scheduling later

n_cg = 6  # TODO note this is hard-coded based on the year


## ----- MODEL VARIABLES ----- ##
model: cp_model.CpModel = cp_model.CpModel()

# partner_of[x] = index of person x's partner
partner_of: List[cp_model.IntVar] = [model.NewIntVar(
    0, n_people - 1, f'partner of {names[i]}({i})') for i in range(n_people)]


## ----- CONSTRAINTS ----- ##
# --- HARD: 1 to 1 pairing, different CG, new pairings (can't be someone you've already been paired with)

# 1 to 1 pairing
model.AddInverse(partner_of, partner_of)
for i in range(n_people):
    model.Add(partner_of[i] != i)

# constraint for different CGs
cg_of_partner_of = [model.NewIntVar(
    1, n_cg, f'CG of partner of {names[i]}({i})') for i in range(n_people)]
for i in range(n_people):
    # cg_of_partner_of[i] == cg_of[partner_of[i]]
    model.AddElement(partner_of[i], cg_of, cg_of_partner_of[i])
    model.Add(cg_of_partner_of[i] != cg_of[i])

# constraint for new pairings
# TODO is there a more efficient way to do this?
for i, old_partners in enumerate(prev_partners):
    for old_partner in old_partners:
        model.Add(partner_of[i] != old_partner)

# --- SOFT: gender preferences, year preferences, scheduling, people we don't want to be paired with

# gender preferences and penalty
N_PENALTIES = 4  # number of different types of penalties, adjusted MANUALLY

gender_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
    f'gender preference of {names[i]}({i}) violated') for i in range(n_people)]
gender_of_partner_of: List[cp_model.IntVar] = [model.NewIntVar(
    0, 1, f'gender of partner of {names[i]}({i})') for i in range(n_people)]
for i in range(n_people):
    if gender_pref[i] != -1:
        model.AddElement(partner_of[i], gender, gender_of_partner_of[i])
        model.Add(gender_of_partner_of[i] == gender_pref[i]).OnlyEnforceIf(
            gender_pref_violated[i].Not())
        # in general, only need one of the reification constraints because we're minimizing violations
    else:
        model.Add(gender_pref_violated[i] == 0)
gender_penalty = model.NewIntVar(0, n_people, 'gender penalty')
model.Add(gender_penalty == sum(gender_pref_violated))

# year preferences and penalty
year_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
    f'year preference of {names[i]}({i}) violated') for i in range(n_people)]
year_of_partner_of: List[cp_model.IntVar] = [model.NewIntVar(
    1, 4, f'year of partner of {names[i]}({i})') for i in range(n_people)]

for i in range(n_people):
    model.AddElement(partner_of[i], year, year_of_partner_of[i])
    model.AddLinearExpressionInDomain(year_of_partner_of[i], cp_model.Domain.FromValues(
        year_pref[i])).OnlyEnforceIf(year_pref_violated[i].Not())
year_penalty = model.NewIntVar(0, n_people, 'year penalty')
model.Add(year_penalty == sum(year_pref_violated))

# scheduling preferences and penalty TODO check
scheduling_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
    f'scheduling preference of {names[i]}({i}) violated') for i in range(n_people)]
for a in range(n_people):
    for b in range(a+1, n_people):
        # intersection is empty set
        if not scheduling_pref[a].intersection(scheduling_pref[b]):
            model.Add(partner_of[a] != b).OnlyEnforceIf(
                scheduling_pref_violated[a].Not())  # no violation => not matched
            model.Add(partner_of[b] != a).OnlyEnforceIf(
                scheduling_pref_violated[b].Not())
scheduling_penalty = model.NewIntVar(0, n_people, 'scheduling penalty')
model.Add(scheduling_penalty == sum(scheduling_pref_violated))


# pairing preferences and penalty
pairing_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
    f'partner preferences of {names[i]}({i}) violated') for i in range(n_people)]
for i in range(n_people):  # TODO is this inefficient? not sure
    model.AddLinearExpressionInDomain(partner_of[i], cp_model.Domain.FromValues(set(
        range(n_people)) - pref_not_partners[i])).OnlyEnforceIf(pairing_pref_violated[i].Not())
pairing_penalty = model.NewIntVar(0, n_people, 'pairing penalty')
model.Add(pairing_penalty == sum(pairing_pref_violated))


total_penalty = model.NewIntVar(0, N_PENALTIES * n_people, f'total penalty')
model.Add(total_penalty == gender_penalty + year_penalty +
          scheduling_penalty + pairing_penalty)


## ----- SOLVE ----- ##
final_pairings: List[Tuple[str, str]] = []
solver = cp_model.CpSolver()


def pretty_print():
    final_pairings = [(names[i], names[solver.Value(partner_of[i])])
                      for i in range(n_people) if i < solver.Value(partner_of[i])]
    print('FINAL PARTNERS:', final_pairings)


def print_penalties():
    print('TOTAL PENALTY:', solver.Value(total_penalty))
    print('Preference violations:')
    for violation_bool in gender_pref_violated + year_pref_violated + scheduling_pref_violated + pairing_pref_violated:
        if solver.Value(violation_bool):
            print('-', violation_bool.Name())


model.Minimize(total_penalty)
result = solver.Solve(model)
if result == cp_model.OPTIMAL or result == cp_model.FEASIBLE:
    pretty_print()
    print_penalties()
else:
    raise ValueError('Not possible!')
'''
