from flask import Flask, request
from matcher import LaddersMatcher
import calendar

# Initializing flask app
app = Flask(__name__)


# fetch data about preferences and previous pairings
@app.route("/people-data", methods=["GET"])
def get_people_data():
    return {
        "people_list": get_legible_data(matcher),
        "prev_pairings": matcher.prev_pairings,
    }


@app.route("/save-matches-txt", methods=["POST"])
def save_to_txt():
    print(request.json["matches"])
    try:
        matcher.save_match_to_txt()
        return {"success": True}
    except:
        return {"success": False}


@app.route("/generate-matching", methods=["POST"])
def generate_matching():
    try:
        matcher.solve()
        matcher.save_match_to_object()
        return {
            "final_pairings": matcher.final_pairings,
            "final_penalties": matcher.final_penalties,
            "sol_found": True,
        }
    except ValueError:
        return {"final_pairings": [], "final_penalties": {}, "sol_found": False}


def get_legible_data(matcher):
    gender_key = {-1: "N/A", 0: "M", 1: "F"}
    year_key = {1: "Freshman", 2: "Sophomore", 3: "Junior", 4: "Senior"}
    cg_key = {1: "1J", 2: "PH", 3: "GS", 4: "TNA", 5: "JB", 6: "LV"}
    num_sched_options = len(LaddersMatcher.SCHEDULING_OPTIONS)
    scheduling_key = {
        i: f"{calendar.day_abbr[i // num_sched_options]} {LaddersMatcher.SCHEDULING_OPTIONS[i % num_sched_options]}"
        for i in range(7 * num_sched_options)
    }
    return [
        {
            "name": matcher.names[i],
            "gender": gender_key[matcher.gender[i]],
            "year": year_key[matcher.year[i]],
            "cg": cg_key[matcher.cg_of[i]],
            "gender_pref": gender_key[matcher.gender_pref[i]],
            "year_pref": [year_key[y] for y in matcher.year_pref[i]],
            "pref_not_partners": [
                matcher.names[p] for p in matcher.pref_not_partners[i]
            ],
            "schedule": [
                scheduling_key[time]
                for time in sorted(list(matcher.scheduling_pref[i]))
            ],
        }
        for i in range(matcher.n_people)
    ]


# Running app
if __name__ == "__main__":
    matcher = LaddersMatcher("people.txt", "previous-matches.txt")
    app.run(debug=True, use_reloader=True, host="localhost", port=8080)
