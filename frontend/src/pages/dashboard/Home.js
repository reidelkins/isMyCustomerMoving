import React, {useState, useEffect} from 'react';
import { Grid, Stack, Container, Typography } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';

import ClientsListCall from '../../redux/calls/ClientsListCall';
import { showLoginInfo } from '../../redux/actions/authActions';
import { companyDashboardData, getCompanyDashboardDataAsync, selectClients } from '../../redux/actions/usersActions';
import Page from '../../components/Page';
import BarChart from '../../components/charts/Bar';
import { StateRevenueDonut } from '../../components/charts/Donut';
import LineChart from '../../components/charts/Line';
import DashboardData from '../../components/DashboardData';

export default function Home() {
  const dispatch = useDispatch();
  // const [totalRevenue, setTotalRevenue] = useState(0);
  // const [totalForSaleLeads, setTotalForSaleLeads] = useState(0);
  // const [totalRecentlySoldLeads, setTotalRecentlySoldLeadsLeads] = useState(0);

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  const dashboardData = useSelector(companyDashboardData);  
  const { retrieved, totalRevenue, revenueByMonth, forSaleByMonth, recentylySoldByMonth } = dashboardData;
  const clientInfo = useSelector(selectClients);
  const { forSale, recentlySold } = clientInfo;

  // useEffect(() => {
  //   if (dashboardData) {
  //     // totalRevenue is the sum of all the revenue values in the array
  //     const totalRevenue = revenue.reduce((a, b) => a + b, 0);
  //     setTotalRevenue(totalRevenue);
  //     // totalLeads is the sum of all the forSale values in the array
  //     const totalForSaleLeads = forSale.reduce((a, b) => a + b, 0);
  //     setTotalForSaleLeads(totalForSaleLeads);
  //     // totalCustomers is the sum of all the recentlySold values in the array
  //     const totalRecentlySoldLeads = recentlySold.reduce((a, b) => a + b, 0);
  //     setTotalRecentlySoldLeadsLeads(totalRecentlySoldLeads);
  //   }
  // }, [dashboardData]);

  useEffect(() => {
    if (userInfo && !retrieved) {
      dispatch(getCompanyDashboardDataAsync());
    }
  }, [userInfo, retrieved, dispatch]);



  return (
    <Page title="Referrals" userInfo={userInfo}>
      {userInfo ? <ClientsListCall /> : null}  
      <Container maxWidth="xl">
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
          <Typography variant="h4" gutterBottom>
            Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
            {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
          </Typography>
        </Stack>        
        <Stack direction="row" spacing={2} marginBottom={8}>
          <DashboardData
            mainText={totalRevenue}
            topText="Total Revenue"
            bottomText={`$36765 The Past 30 Days`}
            color="#85bb65"
            icon="/static/icons/revenue.svg"
          />
          <DashboardData
            mainText={forSale.total+recentlySold.total}
            topText="Total Leads Found"
            bottomText={`177 The Past 30 Days`}
            color="#7BAFD4"
            icon="/static/icons/lead.svg"
          />
          <DashboardData
            mainText={recentlySold.total}
            topText="Customers Moved"
            bottomText={`95 The Past 30 Days`}
            color="#FFC107"
            icon="/static/icons/home.svg"
          />
          <DashboardData
            mainText={forSale.total}
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
