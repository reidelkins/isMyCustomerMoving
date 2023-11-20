/* eslint-disable camelcase */
import { useEffect, useState } from 'react';
import QRCode from 'qrcode';
import * as Yup from 'yup';
import { useDispatch } from 'react-redux';
import { useFormik, Form, FormikProvider } from 'formik';
import { Box, Button, TextField, Dialog, DialogTitle, Stack, Divider, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import { generateQrCodeAsync, verifyOtp, disableTwoFactorAuth } from '../redux/actions/authActions';

const TwoFactorAuth = ({ userInfo }) => {
  const [qrcodeUrl, setqrCodeUrl] = useState('');
  const [open, setOpen] = useState(false);
  const handleClose = () => {
    setOpen(false);
  };
  const dispatch = useDispatch();

  const twoFactorAuthSchema = Yup.object().shape({
    token: Yup.string()
      .required('Token is required')
      .length(6, 'Token must be 6 characters long')
      .matches(/^[0-9]+$/, 'Token must contain only numbers'),
  });

  const formik = useFormik({
    initialValues: {
      token: '',
    },
    validationSchema: twoFactorAuthSchema,
    onSubmit: (values) => {
      dispatch(verifyOtp(values.token));
      setOpen(false);
    },
  });

  const { errors, handleSubmit, getFieldProps } = formik;

  const generateQrCode = async () => {
    dispatch(generateQrCodeAsync());
    setOpen(true);
  };

  useEffect(() => {
    if (userInfo.otp_auth_url) {
      QRCode.toDataURL(userInfo.otp_auth_url).then(setqrCodeUrl);
    }
  }, [userInfo.otp_auth_url]);

  return (
    <div>
      {userInfo.otp_enabled ? (
        <Button
          variant="contained"
          color="primary"
          aria-label="Disable2FA"
          component="label"
          onClick={() => dispatch(disableTwoFactorAuth())}
        >
          Disable 2FA
        </Button>
      ) : (
        <Button
          variant="contained"
          color="primary"
          aria-label="Enable2FA"
          component="label"
          onClick={() => generateQrCode({ email: userInfo.email })}
        >
          Setup 2FA
        </Button>
      )}
      <Dialog open={open} onClose={handleClose} sx={{ padding: '2px', borderRadius: '15px', boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)' }} >
        <DialogTitle>Two-Factor Authentication (2FA)</DialogTitle>
        <Divider />
        <div style={{ padding: '20px', fontSize: '1.2rem' }}>
          <Typography variant="h4" color="primary">
            Configuring An Authenticor App
          </Typography>
          <div style={{ listStyleType: 'decimal', marginTop: '2%' }}>
            <li>Install Google Authenticator (IOS - Android) or Authy (IOS - Android).</li>
            <li>In the authenticator app, select "+" icon.</li>
            <li>Select "Scan a barcode (or QR code)" and use the phone's camera to scan this barcode.</li>
          </div>
          <Typography variant="h5" color="primary" marginTop={3}>
            Scan QR Code
          </Typography>
          <Divider />
          <div>
            <img style={{ width: '40%', height: '40%', objectFit: 'contain' }} src={qrcodeUrl} alt="qrcode url" />
          </div>
          <div>
            <Typography variant="h6" color="primary" marginTop={3}>
              Or Enter Code Into Your App
            </Typography>
            <Divider />
            <p>SecretKey: {userInfo.otp_base32} (Base32 encoded)</p>
          </div>
          <div>
            <Typography variant="h6" color="primary" marginTop={3}>
              Verify Code
            </Typography>
            <Divider />
            <p>For changing the setting, please verify the authentication code:</p>
          </div>
        </div>

        <FormikProvider value={formik}>
          <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
            <Box marginLeft={5}>
              <TextField
                label="Authentication Code"
                margin="normal"
                name="token"
                type="text"
                {...getFieldProps('token')}
                error={Boolean(errors.token)}
                helperText={errors.token}
              />
            </Box>
          </Form>
        </FormikProvider>
        <Stack direction="row" justifyContent="right">
          <Button color="error" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>Submit</Button>
        </Stack>
      </Dialog>
    </div>
  );
};

TwoFactorAuth.propTypes = {
  userInfo: PropTypes.object.isRequired,
};

export default TwoFactorAuth;
