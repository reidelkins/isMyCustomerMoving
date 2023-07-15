import React from 'react';
import { Grid, Stack, Container, Typography } from '@mui/material';
import { useSelector } from 'react-redux';

import { showLoginInfo } from '../../redux/actions/authActions';
import Page from '../../components/Page';
import BarChart from '../../components/charts/Bar';
import { StateRevenueDonut } from '../../components/charts/Donut';
import LineChart from '../../components/charts/Line';
import DashboardData from '../../components/DashboardData';

export default function Home() {
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  return (
    <Page title="Referrals" userInfo={userInfo}>
      <Container maxWidth="xl">
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
          <Typography variant="h4" gutterBottom>
            Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
            {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
          </Typography>
        </Stack>
        {/* <Grid container spacing={1}>
          <Grid item xs={6} md={3}>
            <DashboardData
              mainText="$162299"
              topText="Total Revenue"
              bottomText={`36765 in The Past 30 Days`}
              color="#85bb65"
              icon="/static/icons/revenue.svg"
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <DashboardData
              mainText="819"
              topText="Total Leads Found"
              bottomText={`177 The Past 30 Days`}
              color="#7BAFD4"
              icon="/static/icons/lead.svg"
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <DashboardData
              mainText="509"
              topText="Customers Moved"
              bottomText={`95 The Past 30 Days`}
              color="#FFC107"
              icon="/static/icons/home.svg"
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <DashboardData
              mainText="310"
              topText="Customers Selling"
              bottomText={`82 The Past 30 Days`}
              color="#FF8200"
              icon="/static/icons/for-sale.svg"
            />
          </Grid>
        </Grid>
         */}
        <Stack direction="row" spacing={2} marginBottom={8}>
          <DashboardData
            mainText="$162299"
            topText="Total Revenue"
            bottomText={`36765 in The Past 30 Days`}
            color="#85bb65"
            icon="/static/icons/revenue.svg"
          />
          <DashboardData
            mainText="819"
            topText="Total Leads Found"
            bottomText={`177 The Past 30 Days`}
            color="#7BAFD4"
            icon="/static/icons/lead.svg"
          />
          <DashboardData
            mainText="509"
            topText="Customers Moved"
            bottomText={`95 The Past 30 Days`}
            color="#FFC107"
            icon="/static/icons/home.svg"
          />
          <DashboardData
            mainText="310"
            topText="Customers Selling"
            bottomText={`82 The Past 30 Days`}
            color="#FF8200"
            icon="/static/icons/for-sale.svg"
          />
        </Stack>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <LineChart />
          </Grid>
          <Grid item xs={12} md={4}>
            <StateRevenueDonut />
          </Grid>
          <Grid item xs={12} md={6}>
            <BarChart
              title={'Recently Moved Customers'}
              values={[93, 51, 81, 59, 65, 35, 125]}
              dataLabel={'Recently Moved'}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <BarChart title={'Customers Moving'} values={[15, 25, 11, 39, 53, 41, 126]} dataLabel={'Moving'} />
          </Grid>
        </Grid>
      </Container>
    </Page>
  );
}
