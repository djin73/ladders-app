import './Home.css';
import { useState, useEffect } from "react";
import axios from "axios";
import { Col, Row, Form, Button } from "react-bootstrap";
import { Info } from './Info';
import * as Yup from 'yup';
import { Signup } from "./Signup";
import Dropdown from 'react-dropdown';
import 'react-dropdown/style.css';

export default function AccountPage(props) {
    const [peopleData, setPeopleData] = useState([]);
    const [name, setName] = useState("");
    const [id, setID] = useState("");
    const [gender, setGender] = useState("")
    const [year, setYear] = useState("")
    const [major, setMajor] = useState("")
    const [cg, setCg] = useState("")
    const [genderPref, setGenderPref] = useState([])
    const [yearPref, setYearPref] = useState([])
    const [notPeoplePref, setNotPeoplePref] = useState([])
    const [submit, setSubmit] = useState(false);

    const genderOptions = ['', 'Male', 'Female']
    const defaultGender = genderOptions[0]

    useEffect(() => {
        const fetchData = async () => {
            const response = await axios("/people-data");
            console.log(response);
            setPeopleData(response.data.people_list);
            console.log(response.data);
        };
        fetchData();
    }, []);

    useEffect(() => {
        if (submit) {
            handleSubmit();
        }
    }, [submit]);

    const handleSubmit = (event) => {
        console.log("SUBMIT");
        console.log(name);
        console.log(id);
    };

    const handleNewAccount = (event) => {
        console.log("new account");
    };

    const validate = Yup.object({
        firstName: Yup.string()
            .required('Required'),
        pennID: Yup.string()
            .required("Required"),
    })
    // name, pennID, gender, year, Major, CG
    // Gender preferences, year prefernces, people you don't want to be paired with

    return (
        <div style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '5%' }}>
                <h1>Create New Account</h1>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', alignContent: 'center', marginTop: '1%', width: '40%' }}>
                <Form>
                    <Row className="mb-3">
                        <Form.Group as={Col} controlId="formName">
                            <Form.Label>Name</Form.Label>
                            <Form.Control type="name" placeholder="Enter name" />
                        </Form.Group>

                        <Form.Group as={Col} controlId="formGridPassword">
                            <Form.Label>Penn ID</Form.Label>
                            <Form.Control type="id" placeholder="Penn ID" />
                        </Form.Group>
                    </Row>

                    <Row className="mb-3">

                        <Form.Group as={Col} controlId="formGridState">
                            <Form.Label>Gender</Form.Label>
                            <Form.Select defaultValue="Choose...">
                                <option>Choose...</option>
                                <option>Male</option>
                                <option>Female</option>
                            </Form.Select>
                        </Form.Group>

                        <Form.Group as={Col} controlId="formGridState">
                            <Form.Label>Class</Form.Label>
                            <Form.Select defaultValue="Choose...">
                                <option>Choose...</option>
                                <option>Freshmen</option>
                                <option>Sophomore</option>
                                <option>Junior</option>
                                <option>Senior</option>
                            </Form.Select>
                        </Form.Group>

                        <Form.Group as={Col} controlId="formGridState">
                            <Form.Label>CG</Form.Label>
                            <Form.Select defaultValue="Choose...">
                                <option>Choose...</option>
                                <option>1st Jawn</option>
                                <option>Phillypians</option>
                                <option>Galashines</option>
                                <option>Thessaneveralonians</option>
                                <option>Jonah's Brothers</option>
                                <option>Levitikids</option>
                            </Form.Select>
                        </Form.Group>
                    </Row>

                    {/* <Row className="mb-3">
                        <Form.Group as={Col} controlId="formGridState">
                            <Form.Label>CG</Form.Label>
                            <Form.Select defaultValue="Choose...">
                                <option>Choose...</option>
                                <option>1st Jawn</option>
                                <option>Phillypians</option>
                                <option>Galashines</option>
                                <option>Thessaneveralonians</option>
                                <option>Jonah's Brothers</option>
                                <option>Levitikids</option>
                            </Form.Select>
                        </Form.Group>
                    </Row> */}

                    <Button variant="primary" type="submit">
                        Submit
                    </Button>
                </Form>
            </div>



        </div>
        
    )

    // name, pennID, gender, year, Major, CG
    // Gender preferences, year prefernces, people you don't want to be paired with
    return (
        <div style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '5%' }}>
                <h1>Create New Account</h1>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', alignContent: 'center', marginTop: '5%', width: '40%', paddingBottom: '5%' }}>
                <Signup style={{}} setName={setName} setID={setID} setSubmit={setSubmit} />
                <div style={{ display: 'flex', flexDirection: 'row' }}>
                    <h5 style={{ marginTop: '1%', padding: 0 }}>or </h5>
                    <div id='panel' onClick={handleNewAccount} style={{ display: 'flex', flexDirection: 'row' }}><h5 style={{ marginTop: '1%', padding: 5, borderRadius: 5, textDecorationLine: 'underline' }}>create new account</h5></div>
                </div>
            </div>



        </div>
    );
}
