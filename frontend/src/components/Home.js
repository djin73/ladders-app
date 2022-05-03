import './Home.css';
import { useState, useEffect } from "react";
import axios from "axios";
import { Signup } from "./Signup";

export default function HomePage() {
    const [peopleData, setPeopleData] = useState([]);
    const [name, setName] = useState("");
    const [id, setID] = useState("")
    const [submit, setSubmit] = useState(false)

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
        window.location.href = '/Account'
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', flexDirection:'column', alignItems: 'center'}}>

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '10%' }}>
                <h1 style={{fontSize:100}}>Ladders</h1>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0%' }}>
                <h4>Created by: Daniel Jin and Jonathan Cheng</h4>
            </div>

            {/* <div style={{ display: 'flex', justifyContent: 'center', alignContent: 'center', marginTop: '0%' }}>
                <form style={{ alignSelf: 'center'}}>
                    <label>
                        Name:
                        <input type="text" name="textInput" style={{ width: 400, height: 40, borderRadius: 10}} onChange={(event) => setName(event.target.value)} />
                    </label>
                    <label>
                        Penn ID:
                        <input type="text" name="textInput" style={{ width: 400, height: 40, borderRadius: 10 }} onChange={(event) => setName(event.target.value)} />
                    </label>
                </form>
                <button onClick={handleSubmit} style={{ marginLeft: 10, height: 40, backgroundColor: 'rgb(23,175,100)', borderRadius: 10}}>Analyze</button>
            </div> */}
            
            <div style={{ display: 'flex', flexDirection:'column', alignContent: 'center', marginTop: '5%', width: '40%', paddingBottom: '5%'}}>
                {/* <Signup style={{}} setName={setName} setID={setID} setSubmit={setSubmit}/> */}
                <div style={{ display: 'flex', flexDirection: 'row', alignSelf: 'center'}}>
                    <div id='panel' onClick={handleNewAccount} style={{ display: 'flex', flexDirection: 'row', marginTop: '0.4%'}}><h2 style={{ marginTop: '1%', padding: 5, borderRadius: 5, textDecorationLine: 'underline'}}>create new account</h2></div>
                </div>
            </div>
            


        </div>
    );
}
