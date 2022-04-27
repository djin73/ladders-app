from flask import Flask
from matcher import LaddersMatcher
import calendar

# Initializing flask app
app = Flask(__name__)


# Route for seeing a data
@app.route('/people-data', methods=['GET'])
def get_people_data():
    return get_legible_data(matcher)


def get_legible_data(matcher):
    gender_key = {-1: 'N/A', 0: 'M', 1: 'F'}
    year_key = {1: 'Freshman', 2: 'Sophomore', 3: 'Junior', 4: 'Senior'}
    cg_key = {1: '1J', 2: 'PH', 3: 'GS', 4: 'TNA', 5: 'JB', 6: 'LV'}
    num_sched_options = len(LaddersMatcher.SCHEDULING_OPTIONS)
    scheduling_key = {
        i: f'{calendar.day_abbr[i // num_sched_options]} {LaddersMatcher.SCHEDULING_OPTIONS[i % num_sched_options]}' for i in range(7 * num_sched_options)}
    return {'people_list': [{
        'name': matcher.names[i],
        'gender': gender_key[matcher.gender[i]],
        'year': year_key[matcher.year[i]],
        'cg': cg_key[matcher.cg_of[i]],
        'gender_pref': gender_key[matcher.gender_pref[i]],
        'year_pref': [year_key[y] for y in matcher.year_pref[i]],
        'pref_not_partners': [matcher.names[p] for p in matcher.pref_not_partners[i]],
        'schedule': [scheduling_key[time] for time in matcher.scheduling_pref[i]]
    } for i in range(matcher.n_people)]}
    # {
    #     'names': matcher.names,
    #     'gender': [gender_key[x] for x in matcher.gender],
    #     'year': [year_key[y] for y in matcher.year],
    #     'cg': [cg_key[c] for c in matcher.cg_of],
    #     'gender_pref': [gender_key[x] for x in matcher.gender_pref],
    #     'year_pref': [[year_key[y] for y in prefs] for prefs in matcher.year_pref],
    #     'pref_not_partners': [[matcher.names[i] for i in list] for list in matcher.pref_not_partners],
    #     'schedule': [[scheduling_key[s] for s in sched] for sched in matcher.scheduling_pref]
    # }


# Running app
if __name__ == '__main__':
    matcher = LaddersMatcher("people.txt", "previous-matches.txt")
    app.run(debug=True, use_reloader=True, host="localhost", port=8080)
