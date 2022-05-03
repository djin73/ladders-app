import './Home.css';
import { useState, useEffect } from "react";
import axios from "axios";
import { Col, Row, Form, Button, ToggleButton, ToggleButtonGroup} from "react-bootstrap";

export default function AccountPage(props) {
    const [peopleData, setPeopleData] = useState([]);
    const [name, setName] = useState("");
    const [id, setID] = useState("");
    const [gender, setGender] = useState(-1)
    const [year, setYear] = useState(-1)
    const [major, setMajor] = useState("")
    const [cg, setCg] = useState(-1)
    const [genderPref, setGenderPref] = useState(-1)
    const [yearPref, setYearPref] = useState([])
    const [notPeoplePref, setNotPeoplePref] = useState([])
    const [timePref, setTimePref] = useState([])
    const [submit, setSubmit] = useState(false);
    const [nameDropDown, setNameDropDown] = useState([])
    const [error, setError] = useState(false)
    const [success, setSuccess] = useState(false)

    const genderDict = {
        Male: 0,
        Female: 1
    }
    const yearDict = {
        Freshman: 1,
        Sophomore: 2,
        Junior: 3,
        Senior: 4
    }
    const cgDict = {
        stJawn: 1,
        Phillypians: 2,
        Galashines: 3,
        TNA: 4,
        JonahsBrothers: 5,
        Levitikids: 6
    }
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
        if (peopleData.length > 0) {
            var n = [];
            for (let i = 0; i < peopleData.length; i++) {
                n.push(<option>{peopleData[i].name}</option>);
            }
            setNameDropDown(n);
        }
    }, [peopleData])

    useEffect(() => {
        if (submit) {
            handleSubmit();
        }
    }, [submit]);

    const handleSubmit = (event) => {
        setSuccess(false)
        if (name == "" || id == "" || major == "" || gender == -1 || gender == 'undefined' || year == -1 || year == 'undefined' || cg == -1 || cg == 'undefined') {
            console.log("ERROR")
            setError(true);
        } else {
            setError(false);
            console.log(year)
            const response = axios.post("/write-account", {
                name: name,
                id: id,
                gender: gender,
                year: year,
                major: major,
                cg: cg,
                genderPref: genderPref,
                yearPref: yearPref,
                notPeoplePref: notPeoplePref,
                timePref: timePref
            });
            console.log(response);
            setSuccess(true);

        }
    };

    const handleNotPeoplePref = (l) => {
        var names = []
        for (var element of l) {
            names.push(element.innerText)
        }
        var nums = []
        for (var name of names) {
            for (let i = 0; i < peopleData.length; i++) {
                if (name == peopleData[i].name) {
                    nums.push(i)
                }
            }
        }
        setNotPeoplePref(nums.sort())
    }

    const handleTimePref = (l, day) => {
        var curTimes = timePref;
        for (let i = day*5; i < (day + 1) * 5; i++) {
            if (l.includes(i) && !curTimes.includes(i)) {
                curTimes.push(i)
            } else if (!l.includes(i) && curTimes.includes(i)) {
                curTimes.splice(curTimes.indexOf(i), 1);
            }
        }
        setTimePref(curTimes.sort())
    }


    // name, pennID, gender, year, Major, CG
    // Gender preferences, year prefernces, people you don't want to be paired with

    return (
        <div style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '5%' }}>
                <h1>Create New Account</h1>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', alignContent: 'center', marginTop: '1%', width: '50%' }}>
                <Form>
                    <Row className="mb-3">
                        <Form.Group as={Col} controlId="name">
                            <Form.Label>Name*</Form.Label>
                            <Form.Control type="name" placeholder="Enter name" onChange={e => setName(e.target.value)}/>
                        </Form.Group>

                        <Form.Group as={Col} controlId="pennID">
                            <Form.Label>Penn ID*</Form.Label>
                            <Form.Control type="id" placeholder="Penn ID" onChange={e => setID(e.target.value)}/>
                        </Form.Group>

                        <Form.Group as={Col} controlId="major">
                            <Form.Label>Major*</Form.Label>
                            <Form.Control placeholder="Major" onChange={e => setMajor(e.target.value)} />
                        </Form.Group>
                    </Row>

                    <Row className="mb-3">

                        <Form.Group as={Col} controlId="gender">
                            <Form.Label>Gender*</Form.Label>
                            <Form.Select defaultValue="Choose..." onChange={e => setGender(genderDict[e.target.value])}>
                                <option>Choose...</option>
                                <option>Male</option>
                                <option>Female</option>
                            </Form.Select>
                        </Form.Group>

                        <Form.Group as={Col} controlId="class">
                            <Form.Label>Class*</Form.Label>
                            <Form.Select defaultValue="Choose..." onChange={e => setYear(yearDict[e.target.value])}>
                                <option>Choose...</option>
                                <option>Freshman</option>
                                <option>Sophomore</option>
                                <option>Junior</option>
                                <option>Senior</option>
                            </Form.Select>
                        </Form.Group>

                        <Form.Group as={Col} controlId="cg">
                            <Form.Label>CG*</Form.Label>
                            <Form.Select defaultValue="Choose..." onChange={e => setCg(cgDict[e.target.value.replace(/\W|[0-9]/g, '')])}>
                                <option>Choose...</option>
                                <option>1st Jawn</option>
                                <option>Phillypians</option>
                                <option>Galashines</option>
                                <option>TNA</option>
                                <option>Jonah's Brothers</option>
                                <option>Levitikids</option>
                            </Form.Select>
                        </Form.Group>
                    </Row>

                    <Row>
                        <Col className="m-3">
                            <Form.Group as={Row} controlId="GenderPref">
                                <Form.Label >Gender Preference</Form.Label>
                                <ToggleButtonGroup name= "genPref" defaultValue={[]} onChange={e => setGenderPref(e)}>
                                    <ToggleButton id="Male" value={0} variant="outline-info" className="mx-3">
                                        Male
                                    </ToggleButton>
                                    <ToggleButton id="Female" value={1} variant="outline-info" className="mx-3">
                                        Female
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className="m-3">
                            <Row>
                                <Form.Label>Year Preference</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => setYearPref(e.sort())}>
                                    <ToggleButton id="Freshman" value={1} variant="outline-info" className="mx-3">
                                        Freshman
                                    </ToggleButton>
                                    <ToggleButton id="Sophomore" value={2} variant="outline-info" className="mx-3">
                                        Sophomore
                                    </ToggleButton>
                                    <ToggleButton id="Junior" value={3} variant="outline-info" className="mx-3">
                                        Junior
                                    </ToggleButton>
                                    <ToggleButton id="Senior" value={4} variant="outline-info" className="mx-3">
                                        Senior
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Row>
                        </Col>
                    </Row>

                    <Row className='mb-3'>
                        <Form.Group as={Col} controlId="noPair">
                            <Form.Label>People you would NOT like to be paired with</Form.Label>
                            <Form.Select as="select" multiple onChange={e => handleNotPeoplePref(e.target.selectedOptions)}>
                                {nameDropDown}
                            </Form.Select>
                        </Form.Group>
                    </Row>

                    <Row className='mb-3'>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Sunday">
                                <Form.Label>Sunday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 0)}>
                                    <ToggleButton id="SB" value={0} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="SM" value={1} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="SL" value={2} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="SA" value={3} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="SD" value={4} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Monday">
                                <Form.Label>Monday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 1)}>
                                    <ToggleButton id="MB" value={5} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="MM" value={6} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="ML" value={7} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="MA" value={8} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="MD" value={9} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Tuesday">
                                <Form.Label>Tuesday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 2)}>
                                    <ToggleButton id="TB" value={10} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="TM" value={11} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="TL" value={12} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="TA" value={13} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="TD" value={14} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Wednesday">
                                <Form.Label>Wednesday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 3)}>
                                    <ToggleButton id="WB" value={15} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="WM" value={16} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="WL" value={17} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="WA" value={18} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="WD" value={19} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Thursday">
                                <Form.Label>Thursday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 4)}>
                                    <ToggleButton id="HB" value={20} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="HM" value={21} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="HL" value={22} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="HA" value={23} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="HD" value={24} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Friday">
                                <Form.Label>Friday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 5)}>
                                    <ToggleButton id="FB" value={25} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="FM" value={26} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="FL" value={27} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="FA" value={28} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="FD" value={29} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                        <Col className='m-3'>
                            <Form.Group as={Row} controlId="Saturday">
                                <Form.Label>Saturday</Form.Label>
                                <ToggleButtonGroup type="checkbox" defaultValue={[]} onChange={e => handleTimePref(e.sort(), 6)}>
                                    <ToggleButton id="AB" value={30} variant="outline-info" className="mx-3">
                                        Breakfast
                                    </ToggleButton>
                                    <ToggleButton id="AM" value={31} variant="outline-info" className="mx-3">
                                        Morning
                                    </ToggleButton>
                                    <ToggleButton id="AL" value={32} variant="outline-info" className="mx-3">
                                        Lunch
                                    </ToggleButton>
                                    <ToggleButton id="AA" value={33} variant="outline-info" className="mx-3">
                                        Afternoon
                                    </ToggleButton>
                                    <ToggleButton id="AD" value={34} variant="outline-info" className="mx-3">
                                        Dinner
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Form.Group>
                        </Col>
                    </Row>
                    <Row className="justify-content-md-center">
                        <div style={{ display: 'flex', justifyContent: 'center', color: 'red', width: '100%' }}>
                            <h5>{(error) ? "Please fill in all required information!" : ""} </h5>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'center', color: 'green', width: '100%' }}>
                            <h5>{(success) ? "Successfully updated your information!" : ""} </h5>
                        </div>
                        
                        <Col xs lg="1">
                            
                            <Button variant="primary" md='auto' onClick={handleSubmit}>
                                Submit
                            </Button>
                        </Col>
                        
                    </Row>
                    
                </Form>
            </div>



        </div>
        
    )
}
