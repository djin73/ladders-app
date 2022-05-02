import { Table, Button, Card } from "react-bootstrap";
import { useState, useEffect } from "react";

import axios from "axios";
import "./Dashboard.css";

export default function Dashboard() {
  const [peopleData, setPeopleData] = useState([]);
  const [prevMatches, setPrevMatches] = useState([]);
  const [curMatching, setCurMatching] = useState([]);
  const [curPenalties, setCurPenalties] = useState({});
  const [feasibleSol, setFeasibleSol] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const response = await axios("/people-data");
      console.log(response.data);
      setPeopleData(response.data.people_list);
      setPrevMatches(response.data.prev_pairings);
    };
    fetchData();
  }, []);

  const generateNewMatches = async () => {
    const response = await axios.post("/generate-matching");
    if (curMatching.length) {
      setPrevMatches([...prevMatches, curMatching]);
    }
    setCurMatching(response.data.final_pairings);
    setCurPenalties(response.data.final_penalties);
    setFeasibleSol(response.data.sol_found);
  };

  const saveMatchesToTxt = async () => {
    console.log(curMatching);
    const response = await axios.post("/save-matches-txt", {
      matches: curMatching,
    });
    if (response.data.success) alert("Succesfully saved matches to .txt file!");
    else alert("Error saving matches to .txt file.");
  };

  // helper function to generate list of penalty strings from penalties object
  const getPenaltyStrings = ({ gender, pairing, scheduling, year }) => {
    let genderList = gender.map(
      (id) => `${peopleData[id].name}'s gender preferences were violated`
    );
    let yearList = year.map(
      (id) => `${peopleData[id].name}'s year preferences were violated`
    );
    let schedulingList = scheduling.map(
      (id) => `${peopleData[id].name}'s scheduling preferences were violated`
    );
    let pairingList = pairing.map(
      (id) =>
        `${peopleData[id].name} was paired with someone they requested not to be paired with`
    );
    return genderList.concat(yearList, schedulingList, pairingList);
  };

  return (
    <div className="container">
      <h1 className="header">Ladders Dashboard</h1>
      <Button variant="secondary" onClick={generateNewMatches} size="lg">
        Generate New Matches!
      </Button>
      {curMatching.length || !feasibleSol ? (
        <div>
          <Card className="matchingCard" style={{ backgroundColor: "#d3e0f5" }}>
            {feasibleSol ? (
              <Card.Body>
                <Card.Title>New Matching </Card.Title>
                <Table
                  responsive
                  bordered
                  size="sm"
                  style={{ border: "1px black" }}
                >
                  <tbody>
                    <tr>
                      {curMatching.map((pair) => (
                        <td>{pair[0]}</td>
                      ))}
                    </tr>
                    <tr>
                      {curMatching.map((pair) => (
                        <td>{pair[1]}</td>
                      ))}
                    </tr>
                  </tbody>
                </Table>
                <Card.Text>Penalties:</Card.Text>
                <ul>
                  {getPenaltyStrings(curPenalties).map((str) => (
                    <li>{str}</li>
                  ))}
                </ul>
                <Button variant="secondary" onClick={saveMatchesToTxt}>
                  Save Matching to .txt file
                </Button>
              </Card.Body>
            ) : (
              <Card.Body>
                <Card.Title>Not possible!</Card.Title>
              </Card.Body>
            )}
          </Card>
        </div>
      ) : null}

      <hr></hr>
      <h3 className="smallHeader">Previous matches:</h3>
      {prevMatches
        .slice()
        .reverse()
        .map((list_of_pairs) => {
          return (
            <div className="matching">
              <Table responsive bordered size="sm">
                <tbody>
                  <tr>
                    {list_of_pairs.map((pair) => (
                      <td>{pair[0]}</td>
                    ))}
                  </tr>
                  <tr>
                    {list_of_pairs.map((pair) => (
                      <td>{pair[1]}</td>
                    ))}
                  </tr>
                </tbody>
              </Table>
            </div>
          );
        })}
      <hr></hr>
      <h3 className="smallHeader">User info:</h3>
      <Table striped bordered hover responsive="md">
        <thead>
          <tr>
            <th>#</th>
            <th>Name</th>
            <th>Gender</th>
            <th>Year</th>
            <th>Small Group</th>
            <th>Gender Prefs</th>
            <th>Year Prefs</th>
            <th>Preferred Not Partners</th>
            <th>Availabilities</th>
          </tr>
        </thead>
        <tbody>
          {peopleData.map(
            (
              {
                name,
                gender,
                year,
                cg,
                gender_pref,
                year_pref,
                pref_not_partners,
                schedule,
              },
              idx
            ) => {
              return (
                <tr key={idx}>
                  <td>{idx}</td>
                  <td>{name}</td>
                  <td>{gender}</td>
                  <td>{year}</td>
                  <td>{cg}</td>
                  <td
                    style={
                      curPenalties["gender"] &&
                      curPenalties["gender"].includes(idx)
                        ? { backgroundColor: "#f0b6b1" }
                        : {}
                    }
                  >
                    {gender_pref}
                  </td>
                  <td
                    style={
                      curPenalties["year"] && curPenalties["year"].includes(idx)
                        ? { backgroundColor: "#f0b6b1" }
                        : {}
                    }
                  >
                    {year_pref.join(", ")}
                  </td>
                  <td
                    style={
                      curPenalties["pairing"] &&
                      curPenalties["pairing"].includes(idx)
                        ? { backgroundColor: "#f0b6b1" }
                        : {}
                    }
                  >
                    {pref_not_partners.join(", ")}
                  </td>
                  <td
                    style={
                      curPenalties["scheduling"] &&
                      curPenalties["scheduling"].includes(idx)
                        ? { backgroundColor: "#f0b6b1", fontSize: "11px" }
                        : { fontSize: "11px" }
                    }
                  >
                    {schedule.join(", ")}
                  </td>
                </tr>
              );
            }
          )}
        </tbody>
      </Table>
    </div>
  );
}
