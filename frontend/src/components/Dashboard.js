import { Table } from "react-bootstrap";
import { useState, useEffect } from "react";
import axios from "axios";

export default function Dashboard() {
  const [peopleData, setPeopleData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const response = await axios("/people-data");
      console.log(response);
      setPeopleData(response.data.people_list);
      console.log(response.data);
    };
    fetchData();
  }, []);

  return (
    <div>
      <Table striped bordered hover>
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
                <tr>
                  <td>{idx}</td>
                  <td>{name}</td>
                  <td>{gender}</td>
                  <td>{year}</td>
                  <td>{cg}</td>
                  <td>{gender_pref}</td>
                  <td>{year_pref.join(", ")}</td>
                  <td>{pref_not_partners.join(", ")}</td>
                  <td>{schedule.join(", ")}</td>
                </tr>
              );
            }
          )}
        </tbody>
      </Table>
    </div>
  );
}
