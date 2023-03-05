import * as Yup from 'yup';
import { useEffect } from "react";
import { styled } from '@mui/material/styles';
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { useFormik, Form, FormikProvider } from 'formik';

import { Box, TextField, Button, Stack, Card, Typography, Container } from "@mui/material";
// import { LoadingButton } from "../components/LoadingButton";
import { showLoginInfo, validateOtp } from '../redux/actions/authActions';
import useResponsive from '../hooks/useResponsive';
import Page from '../components/Page';
import Logo from '../components/Logo';

const RootStyle = styled('div')(({ theme }) => ({
  [theme.breakpoints.up('md')]: {
    display: 'flex',
  },
}));

const HeaderStyle = styled('header')(({ theme }) => ({
  top: 0,
  zIndex: 9,
  lineHeight: 0,
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  position: 'absolute',
  padding: theme.spacing(3),
  justifyContent: 'space-between',
  [theme.breakpoints.up('md')]: {
    alignItems: 'flex-start',
    padding: theme.spacing(7, 5, 0, 7),
  },
}));

const SectionStyle = styled(Card)(({ theme }) => ({
  width: '100%',
  maxWidth: 464,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  margin: theme.spacing(2, 0, 2, 2),
}));

const ContentStyle = styled('div')(({ theme }) => ({
  maxWidth: 480,
  margin: 'auto',
  minHeight: '100vh',
  display: 'flex',
  justifyContent: 'center',
  flexDirection: 'column',
  padding: theme.spacing(12, 0),
}));

export default function Validate2fa(){
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const mdUp = useResponsive('up', 'md');

  const userLogin = useSelector(showLoginInfo);
  const {userInfo, twoFA } = userLogin;

  const twoFactorAuthSchema = Yup.object().shape({
    token: Yup.string()
        .required("Token is required")
        .length(6, "Token must be 6 characters long")
        .matches(/^[0-9]+$/, "Token must contain only numbers"),
    });

    const formik = useFormik({
    initialValues: {
        token: "",
    },
    validationSchema: twoFactorAuthSchema,
    onSubmit: (values) => {
        console.log("Verify OTP", values.token);
        dispatch(validateOtp(values.token));
    },
    });

    const { errors, handleSubmit, getFieldProps } = formik;

    useEffect(() => {
      if (userInfo) {
        if (twoFA) {
          navigate("/dashboard/customers")
        }
      } else {
        navigate("/login")
      }
    }, [userInfo, twoFA])

  return (
    <Page title="Validate 2FA">
      <RootStyle>
        <HeaderStyle>
          <Logo />
        </HeaderStyle>
        {mdUp && (
          <SectionStyle>
            <Typography variant="h3" sx={{ px: 5, mt: 10, mb: 5 }}>
              Verify With Your Authenticator App
            </Typography>
            <img alt="register" src="/static/illustrations/illustration_register.png" />
          </SectionStyle>
        )}
        <Container>
          <ContentStyle>
            <Typography variant="h2" gutterBottom>
              Enter The 6 Digit Code
            </Typography>

            <Typography sx={{ color: 'text.secondary', mb: 5 }}> </Typography>

            <FormikProvider value={formik} >
              <Form autoComplete="off" noValidate onSubmit={handleSubmit} >
                  <Box marginLeft={5}>
                      <TextField
                      label="Authentication Code"
                      margin="normal"
                      name="token"
                      type="text"
                      {...getFieldProps("token")}
                      error={Boolean(errors.token)}
                      helperText={errors.token}
                      
                  />
                  </Box>
                  
              </Form>
            </FormikProvider>
            <Stack direction="row" justifyContent="center">
                <Button onClick={handleSubmit}>Verify</Button>
            </Stack>
            

            
          </ContentStyle>
        </Container>        
      </RootStyle>
    </Page>
  );
};

