import { Grid, Container, Typography, Card, CardContent, Box, Button, CardActions, Link } from '@mui/material';
// components
import Page from '../components/Page';

// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'employee', label: 'Name', alignRight: false },
  { id: 'role', label: 'Role', alignRight: false },
  { id: 'status', label: 'Status', alignRight: false },
];


export default function ProfileSettings() {
  return (
    <Page title="Profile Settings">
      <Container maxWidth="xl">
        <Typography variant="h4" sx={{ mb: 5 }}>
          Hi, Welcome 👋
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={8}>
            <h1>Test</h1>
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <h2>Test 2</h2>
          </Grid>
        </Grid>

        
      </Container>
    </Page>
  );
}
