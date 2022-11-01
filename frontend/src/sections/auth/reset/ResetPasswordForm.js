import * as Yup from 'yup';
import { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useFormik, Form, FormikProvider } from 'formik';
// @mui

import { Link, Stack, TextField, IconButton, InputAdornment, Alert, AlertTitle } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useSelector, useDispatch } from 'react-redux';

import { resetRequest } from '../../../redux/actions/authActions';

// ----------------------------------------------------------------------

export default function ResetPasswordForm() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userLogin = useSelector((state) => state.userLogin);
  const { error: loginError, loading: loginLoading, userInfo } = userLogin;

  const ResetPasswordSchema = Yup.object().shape({
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
    company: Yup.string().required('Company name is required'),
  });

  const formik = useFormik({
    initialValues: {
      email: '',
      company: '',
    },
    validationSchema: ResetPasswordSchema,
    onSubmit: () => {
      dispatch(resetRequest(values.email, values.company));
    },
  });

  const { errors, touched, values, isSubmitting, handleSubmit, getFieldProps } = formik;

  useEffect(() => {
    if (userInfo) {
      navigate('/login', { replace: true });
    }
  }, [navigate, userInfo]);
  return (
    <FormikProvider value={formik}>
      <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Company"
            {...getFieldProps('company')}
            error={Boolean(touched.company && errors.company)}
            helperText={touched.company && errors.company}
          />

          <TextField
            fullWidth
            autoComplete="username"
            type="email"
            label="Email address"
            {...getFieldProps('email')}
            error={Boolean(touched.email && errors.email)}
            helperText={touched.email && errors.email}
          />
        </Stack>

        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ my: 2 }}>
          <Link component={RouterLink} variant="subtitle2" to="/login" underline="hover">
            Return to login
          </Link>
        </Stack>
        {loginError ? (
          <Alert severity="error">
            <AlertTitle>Reset Password Error</AlertTitle>
            {loginError}
          </Alert>
        ) : null}

        <LoadingButton
          fullWidth
          size="large"
          type="submit"
          variant="contained"
          loading={loginLoading ? isSubmitting : null}
        >
          Submit Info
        </LoadingButton>
      </Form>
    </FormikProvider>
  );
}
