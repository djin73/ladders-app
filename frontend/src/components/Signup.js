import React from 'react';
import { Formik, Form } from 'formik';
import { TextField } from './TextField';
import * as Yup from 'yup';
import { propTypes } from 'react-bootstrap/esm/Image';

export const Signup = (props) => {
    const validate = Yup.object({
        firstName: Yup.string()
            .required('Required'),
        pennID: Yup.string()
            .required("Required")
    })

    return (
        <Formik
            initialValues={{
                firstName: '',
                pennID: ''
            }}
            validationSchema={validate}
            onSubmit={values => {
                props.setName(values.firstName)
                props.setID(values.pennID)
                props.setSubmit(true)
            }}
        >
            {formik => (
                <div>
                    {/* <h1 className="my-4 font-weight-bold .display-4">Sign In</h1> */}
                    <Form>
                        <TextField label="Name" name="firstName" type="text" />
                        <TextField label="Penn ID" name="pennID" type="text" />
                        <button className="btn btn-primary mt-3" type="submit">Log In!</button>
                    </Form>
                </div>
            )}
        </Formik>
    )
}
