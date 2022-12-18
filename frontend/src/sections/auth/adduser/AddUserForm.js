import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';
import { useState } from 'react';
import PropTypes from 'prop-types';
// material
import { Stack, TextField, Alert, AlertTitle, InputAdornment, IconButton } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useDispatch, useSelector } from 'react-redux';
import {useNavigate } from 'react-router-dom';

import { showLoginInfo, showRegisterInfo, addUserAsync } from '../../../redux/actions/authActions';

import Iconify from '../../../components/Iconify';


// component

// ----------------------------------------------------------------------

AddUserForm.propTypes = {
  token: PropTypes.string,
};

export default function AddUserForm({token}) {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userRegister = useSelector(showRegisterInfo);
  const { error: registerError, loading: registerLoading } = userRegister;

  const [showPassword, setShowPassword] = useState(false);

  const AddUserSchema = Yup.object().shape({
    firstName: Yup.string().min(2, 'Too Short!').max(50, 'Too Long!').required('First name required'),
    lastName: Yup.string().min(2, 'Too Short!').max(50, 'Too Long!').required('Last name required'),
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
    password: Yup.string().min(6, 'Password is too short - should be 6 chars minimum.').required('Password is required'),
  });

  const formik = useFormik({
    initialValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      token
    },
    validationSchema: AddUserSchema,
    onSubmit: () => {
      console.log("sup")
      dispatch(addUserAsync(values.firstName, values.lastName, values.email, values.password, values.token));
      navigate('/login', { replace: true });
    },
  });

  const { errors, touched, values, handleSubmit, isSubmitting, getFieldProps } = formik;
  
  return (
    <FormikProvider value={formik}>
      <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
        <Stack spacing={3}>  
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>

            <TextField
              fullWidth
              label="First name"
              {...getFieldProps('firstName')}
              error={Boolean(touched.firstName && errors.firstName)}
              helperText={touched.firstName && errors.firstName}
            />

            <TextField
              fullWidth
              label="Last name"
              {...getFieldProps('lastName')}
              error={Boolean(touched.lastName && errors.lastName)}
              helperText={touched.lastName && errors.lastName}
            />
          </Stack>

          <TextField
            fullWidth
            autoComplete="username"
            type="email"
            label="Email address"
            {...getFieldProps('email')}
            error={Boolean(touched.email && errors.email)}
            helperText={touched.email && errors.email}
          />
          <TextField
            fullWidth
            autoComplete="current-password"
            type={showPassword ? 'text' : 'password'}
            label="Password"
            {...getFieldProps('password')}
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

          {registerError ? (
            <Alert severity="error">
              <AlertTitle>Register Error</AlertTitle>
              {registerError}
            </Alert>
          ) : null}

          <LoadingButton
            fullWidth
            size="large"
            type="submit"
            variant="contained"
            loading={registerLoading ? isSubmitting : null}
          >
            Create New Account
          </LoadingButton>
        </Stack>
      </Form>
    </FormikProvider>
  );
}
