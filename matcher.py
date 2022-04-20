from ortools.sat.python import cp_model
from typing import List, Set, Tuple

from regex import E


# TODO: consolidate everything into a class later
class LaddersMatcher:

    def __init__(self):
        self.x = 1

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


# --- SOFT: gender preferences, year preferences, scheduling (could just be like Monday mornings), people we don't want to be paired with

# gender preferences and penalty
N_PENALTIES = 3  # number of different types of penalties TODO ALWAYS change this manually

gender_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
    f'gender preference of {names[i]}({i}) violated') for i in range(n_people)]
gender_of_partner_of: List[cp_model.IntVar] = [model.NewIntVar(
    0, 1, f'gender of partner of {names[i]}({i})') for i in range(n_people)]
for i in range(n_people):
    if gender_pref[i] != -1:
        model.AddElement(partner_of[i], gender, gender_of_partner_of[i])
        model.Add(gender_of_partner_of[i] == gender_pref[i]).OnlyEnforceIf(
            gender_pref_violated[i].Not())
        # we should only need one of the reification constraints because we're minimizing violations
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

# TODO implement scheduling later
# scheduling_violated: List[cp_model.IntVar] = [model.NewBoolVar(f'scheduling preference of {names[i]}({i}) violated') for i in range(n_people)]

# pairing preferences and penalty
pairing_pref_violated: List[cp_model.IntVar] = [model.NewBoolVar(
    f'partner preferences of {names[i]}({i}) violated') for i in range(n_people)]
for i in range(n_people):  # TODO is this inefficient? not sure
    model.AddLinearExpressionInDomain(partner_of[i], cp_model.Domain.FromValues(set(
        range(n_people)) - pref_not_partners[i])).OnlyEnforceIf(pairing_pref_violated[i].Not())
pairing_penalty = model.NewIntVar(0, n_people, 'pairing penalty')
model.Add(pairing_penalty == sum(pairing_pref_violated))


total_penalty = model.NewIntVar(0, N_PENALTIES * n_people, f'total penalty')
model.Add(total_penalty == gender_penalty + year_penalty + pairing_penalty)


## ----- SOLVE ----- ##
final_pairings: List[Tuple[str, str]] = []


def pretty_print():
    final_pairings = [(names[i], names[solver.Value(partner_of[i])])
                      for i in range(n_people) if i < solver.Value(partner_of[i])]
    print('FINAL PARTNERS:', final_pairings)


model.Minimize(total_penalty)
solver = cp_model.CpSolver()
result = solver.Solve(model)
if result == cp_model.OPTIMAL or result == cp_model.FEASIBLE:
    pretty_print()
    print('Penalty:', solver.Value(total_penalty))
else:
    raise ValueError('Not possible!')
