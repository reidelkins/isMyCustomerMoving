import { Container, Typography, Link } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link as RouterLink } from 'react-router-dom';

// hooks
import { AddUserForm } from '../sections/auth/adduser';
import useResponsive from '../hooks/useResponsive';

// components
import Page from '../components/Page';


// ----------------------------------------------------------------------

const ContentStyle = styled('div')(({ theme }) => ({
  maxWidth: 480,
  margin: 'auto',
  minHeight: '100vh',
  display: 'flex',
  justifyContent: 'center',
  flexDirection: 'column',
  padding: theme.spacing(12, 0),
}));

export default function AddUser() {
  const smUp = useResponsive('up', 'sm');
  return (
    <Page title="AddUser">
        
      <Container>
          <ContentStyle>
            <Typography variant="h2" gutterBottom>
              Add User
            </Typography>

            <Typography sx={{ color: 'text.secondary', mb: 5 }}> </Typography>

            <AddUserForm />

            {!smUp && (
              <Typography variant="body2" sx={{ mt: 3, textAlign: 'center' }}>
                Already have an account?{' '}
                <Link variant="subtitle2" to="/login" component={RouterLink}>
                  Login
                </Link>
              </Typography>
            )}
          </ContentStyle>
        </Container>
    </Page>
  );
}
