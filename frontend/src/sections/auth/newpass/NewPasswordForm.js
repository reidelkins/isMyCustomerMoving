import * as Yup from 'yup';
import { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom';
import { useFormik, Form, FormikProvider } from 'formik';
// @mui

import { Link, Stack, TextField, IconButton, InputAdornment, Alert, AlertTitle } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useSelector, useDispatch } from 'react-redux';
import Iconify from '../../../components/Iconify';

import { submitNewPass } from '../../../redux/actions/authActions';

// ----------------------------------------------------------------------

export default function NewPasswordForm() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { token } = useParams();

  const userLogin = useSelector((state) => state.userLogin);
  const { error: loginError, loading: loginLoading, userInfo } = userLogin;

  const [showPassword, setShowPassword] = useState(false);

  const NewPasswordSchema = Yup.object().shape({
    password: Yup.string().required('Please Enter your password')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})/,
      "Must Contain 8 Characters, One Uppercase, One Lowercase, One Number and One Special Case Character"
    ),
    verifiedPassword: Yup.string()
     .oneOf([Yup.ref('password'), null], 'Passwords must match'),
  });

  const formik = useFormik({
    initialValues: {
      password: '',
      verifiedPassword: '',
    },
    validationSchema: NewPasswordSchema,
    onSubmit: () => {
      dispatch(submitNewPass(values.password, token));
      navigate('/login', { replace: true });
    },
  });

  const { errors, touched, values, isSubmitting, handleSubmit, getFieldProps } = formik;

  return (
    <FormikProvider value={formik}>
      <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
        <Stack spacing={3}>
          <TextField
            fullWidth
            type={showPassword ? 'text' : 'password'}
            label="New Password"
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
          <TextField
            fullWidth
            type={'password'}
            label="Verify New Password"
            {...getFieldProps('verifiedPassword')}
            error={Boolean(touched.verifiedPassword && errors.verifiedPassword)}
            helperText={touched.verifiedPassword && errors.verifiedPassword}
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
          Submit New Password
        </LoadingButton>
      </Form>
    </FormikProvider>
  );
}
