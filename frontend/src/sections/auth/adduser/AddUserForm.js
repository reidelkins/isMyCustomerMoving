import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';
// material
import { Stack, TextField, Alert, AlertTitle } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useDispatch, useSelector } from 'react-redux';
import {useNavigate } from 'react-router-dom';

import { addUser } from '../../../redux/actions/usersActions';

// import { addUser } from '../../../redux/actions/userActions';

// component

// ----------------------------------------------------------------------

export default function RegisterForm() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userRgister = useSelector((state) => state.userRgister);
  const { error: registerError, loading: registerLoading } = userRgister;

  const AddUserSchema = Yup.object().shape({
    firstName: Yup.string().min(2, 'Too Short!').max(50, 'Too Long!').required('First name required'),
    lastName: Yup.string().min(2, 'Too Short!').max(50, 'Too Long!').required('Last name required'),
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
  });

  const formik = useFormik({
    initialValues: {
      firstName: '',
      lastName: '',
      email: '',
    },
    validationSchema: AddUserSchema,
    onSubmit: () => {
      console.log("sup")
      dispatch(addUser(values.firstName, values.lastName, values.email));
      navigate('/dashboard/user', { replace: true });
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
            Add User
          </LoadingButton>
        </Stack>
      </Form>
    </FormikProvider>
  );
}
