from ortools.sat.python import cp_model
from typing import List, Set


class LaddersMatcher:

    def __init__(self):
        self.x = 1

## ----- INPUTS ----- ##


# gender[x] = gender of person x; -1 = neither, 0 = male, 1 = female
gender: List[int] = []
gender_pref: List[int] = []

# year[x] = year of person x; 0 = freshman, 1 = sophomore, 2 = junior, 3 = senior+
year: List[int] = []

# year_pref[x] = preferred year(s) to be matched to
year_pref: List[List[int]] = []

# cg_of[x] = the participant's CG
cg_of: List[int] = []

# prev_partners[x] = list of people that x has been paired with previously (most recent first?)
prev_partners: List[List[int]] = []

pref_not_paired_with: List[Set[int]] = []

# TODO: Don't forget to account number of people eventually (odd)
# TODO: incoroporate stuff like major/school into profile
# TODO: worry about scheduling later
n_people = len(year)

## ----- MODEL VARIABLES ----- ##
# partner_of[x] = index of person x's partner
partner_of: List[cp_model.IntVar] = []

## ----- CONSTRAINTS ----- ##
model: cp_model.CpModel = cp_model.CpModel()
# --- HARD: 1 to 1 pairing, different CG, new pairings (can't be someone you've already been paired with)
model.AddInverse(partner_of, partner_of)

# add constraint for different CG
# add constraint for new pairing

# --- SOFT: gender preferences, year preferences, scheduling (could just be like Monday mornings), people we don't want to be paired with
