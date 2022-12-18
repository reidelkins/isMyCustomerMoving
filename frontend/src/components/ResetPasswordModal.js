import React, {useState} from 'react';
import * as Yup from 'yup';
import {
    Button,
    TextField,
    Dialog,
    DialogTitle,
    Stack, 
    InputAdornment,
    IconButton,
} from '@mui/material';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch } from 'react-redux';

import { resetPasswordAsync } from '../redux/actions/authActions';
import Iconify from './Iconify';


export default function ResetPasswordModal() {
    const [open, setOpen] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const dispatch = useDispatch();
    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };

    const ChangePasswordSchema = Yup.object().shape({
        oldPassword: Yup.string().email('Email must be a valid email address').required('Email is required'),
        password: Yup.string().required('Password is required').matches(
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})/,
            "Must Contain 8 Characters, One Uppercase, One Lowercase, One Number and One Special Case Character"
            ),
        verifiedPassword: Yup.string()
            .oneOf([Yup.ref('password'), null], 'Passwords must match'),
    });
    
    const formik = useFormik({
        initialValues: {
            oldPassword: '',
            password: '',
            verifiedPassword: '',
        },
        validationSchema: ChangePasswordSchema,
        onSubmit: () => {
            dispatch(resetPasswordAsync(values.oldPassword, values.password));
            setOpen(false);
        },
    });

    const { errors, touched, values, handleSubmit, getFieldProps } = formik;
  return (
    <div>
        <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
            Change Password
        </Button>
        <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
            <DialogTitle>Add a User</DialogTitle>
            <FormikProvider value={formik}>
                <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                    <Stack spacing={3}>
                        <TextField
                            fullWidth
                            autoComplete="current-password"
                            type={showPassword ? 'text' : 'password'}
                            label="Password"
                            {...getFieldProps('oldPassword')}
                            InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                <IconButton edge="end" onClick={() => setShowPassword((prev) => !prev)}>
                                    <Iconify icon={showPassword ? 'eva:eye-fill' : 'eva:eye-off-fill'} />
                                </IconButton>
                                </InputAdornment>
                            ),
                            }}
                            error={Boolean(touched.password && errors.password)}
                            helperText={touched.password && errors.password}
                        />
                    </Stack>
                </Form>
            </FormikProvider>
            <Stack direction="row" justifyContent="right">
                <Button color="error" onClick={handleClose}>Cancel</Button>
                <Button onClick={handleSubmit}>Reset</Button>
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