import * as Yup from 'yup';
import { useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useFormik, Form, FormikProvider } from 'formik';
import PropTypes from 'prop-types';

// @mui
import { Link, Stack, TextField } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { useSelector, useDispatch } from 'react-redux';

import { resetAsync, showLoginInfo, showRegisterInfo } from '../../../redux/actions/authActions';

// ----------------------------------------------------------------------

ResetPasswordForm.propTypes = {
  setSubmitted: PropTypes.func
};

export default function ResetPasswordForm({setSubmitted}) {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userResetRequest = useSelector(showRegisterInfo);
  const { loading: resetRequestLoading } = userResetRequest;
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const ResetPasswordSchema = Yup.object().shape({
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
  });

  const formik = useFormik({
    initialValues: {
      email: '',
    },
    validationSchema: ResetPasswordSchema,
    onSubmit: () => {
      setSubmitted(true);
      dispatch(resetAsync(values.email));
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

        <LoadingButton
          fullWidth
          size="large"
          type="submit"
          variant="contained"
          loading={resetRequestLoading ? isSubmitting : null}
        >
          Submit Info
        </LoadingButton>
      </Form>
    </FormikProvider>
  );
}
