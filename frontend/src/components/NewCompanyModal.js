import React from 'react';
import * as Yup from 'yup';
import {
    Button,
    TextField,
    Dialog,
    DialogTitle,
    Stack
} from '@mui/material';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch } from 'react-redux';

import { createCompany } from '../redux/actions/usersActions';


export default function NewCompanyModal() {
    // const classes = useStyles();
    const [open, setOpen] = React.useState(false);
    const dispatch = useDispatch();
    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };

    const NewCompanySchema = Yup.object().shape({
        company: Yup.string().required('Company Name is required'),
        email: Yup.string().email('Email must be a valid email address').required('Email is required'),
    });
    
    const formik = useFormik({
        initialValues: {
        company: '',
        email: '',
        },
        validationSchema: NewCompanySchema,
        onSubmit: () => {
            dispatch(createCompany(values.company, values.email));
            values.company = '';
            values.email = '';
            setOpen(false);
        },
    });

    const { errors, touched, values, handleSubmit, getFieldProps } = formik;
    return (
        <div>
            <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
                Create Company
            </Button>
            <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
                <DialogTitle>Create a Company</DialogTitle>
                <FormikProvider value={formik}>
                    <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                        <Stack spacing={3}>
                            <TextField
                                fullWidth
                                label="Company Name"
                                placeholder="Company Name"
                                {...getFieldProps('company')}
                                error={Boolean(touched.company && errors.company)}
                                helperText={touched.company && errors.company}
                            />
                            <TextField
                                fullWidth
                                // type="email"
                                label="Admin Email"
                                placeholder="Email"
                                {...getFieldProps('email')}
                                error={Boolean(touched.email && errors.email)}
                                helperText={touched.email && errors.email}
                            />
                        </Stack>
                    </Form>
                </FormikProvider>
                <Stack direction="row" justifyContent="right">
                    <Button color="error" onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleSubmit}>Submit</Button>
                </Stack>
                

            </Dialog>
            {/* <Fade in={open}>
                <Dialog open={open} onClose={handleClose}>
                    <DialogTitle>Subscribe</DialogTitle>
                    <DialogContent>
                    <DialogContentText>
                        To subscribe to this website, please enter your email address here. We
                        will send updates occasionally.
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="name"
                        label="Email Address"
                        type="email"
                        fullWidth
                        variant="standard"
                    />
                    </DialogContent>
                    <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleClose}>Subscribe</Button>
                    </DialogActions>
                </Dialog>
            </Fade> */}
        </div>
    );
}