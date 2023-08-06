import React, { useEffect, useState} from 'react';
import { Button, Grid, Stack, Container, Typography, Tooltip} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';

import ClientsListCall from '../../redux/calls/ClientsListCall';
import { showLoginInfo } from '../../redux/actions/authActions';
import { companyDashboardData, getCompanyDashboardDataAsync, selectClients } from '../../redux/actions/usersActions';
import Page from '../../components/Page';
import BarChart from '../../components/charts/Bar';
import Speedometer from '../../components/charts/Speedometer';
import LineChart from '../../components/charts/Line';
import DashboardData from '../../components/cards/DashboardData';
import ROICard from '../../components/cards/ROICard';

export default function Home() {
  const dispatch = useDispatch();

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  const dashboardData = useSelector(companyDashboardData);  
  const { retrieved, monthsActive, totalRevenue, revenueByMonth, forSaleByMonth, recentlySoldByMonth, customerRetention, clientsAcquired, clientsAcquiredByMonth } = dashboardData;
  
  const clientInfo = useSelector(selectClients);
  const { forSale, recentlySold } = clientInfo;

  const [allClients, setAllClients] = useState(true);
  const [allClientCustomerRetention, setAllClientCustomerRetention] = useState(0);
  const [revClientCustomerRetention, setRevClientCustomerRetention] = useState(0);

  useEffect(() => {
    if (userInfo && retrieved) {      
      setAllClientCustomerRetention(Math.ceil((customerRetention.locations_with_new_address / customerRetention.new_address_total)*100));
      setRevClientCustomerRetention(Math.ceil((customerRetention.customers_with_new_address_and_revenue / customerRetention.new_address_with_revenue)*100));
    }
  }, [userInfo, retrieved, dashboardData, customerRetention]);

  useEffect(() => {
    if (userInfo && !retrieved) {
      dispatch(getCompanyDashboardDataAsync());
    }
  }, [userInfo, retrieved, dispatch]);

  return (
    <Page title="Home" userInfo={userInfo}>
      {userInfo ? <ClientsListCall /> : null}  
      <Container maxWidth="xl">
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
          <Typography variant="h4" gutterBottom data-testid="welcome-message">
            Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
            {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
          </Typography>
        </Stack>        
        <Stack direction="row" spacing={2} marginBottom={8}>
          <DashboardData
            mainText={totalRevenue}
            topText="Total Revenue"
            bottomText={`${parseFloat(Object.values(revenueByMonth)[0]).toFixed(2)} This Month`}
            color="#85bb65"
            icon="/static/icons/revenue.svg"
          />
          <DashboardData
            mainText={clientsAcquired}
            topText="Clients Acquired"
            bottomText={`${Object.values(clientsAcquiredByMonth)[0]} This Month`}
            color="#7BAFD4"
            icon="/static/icons/lead.svg"
          />
          <DashboardData
            mainText={recentlySold.total}
            topText="Customers Moved"
            bottomText={`${Object.values(recentlySoldByMonth)[0]} This Month`}
            color="#FFC107"
            icon="/static/icons/home.svg"
          />
          <DashboardData
            mainText={forSale.total}
            topText="Customers Selling"
            bottomText={`${Object.values(forSaleByMonth)[0]} This Month`}
            color="#FF8200"
            icon="/static/icons/for-sale.svg"
          />
        </Stack>
        <Grid container spacing={2}>
          {userInfo.company.crm === "ServiceTitan" && (
            <>
              <Grid item xs={12} md={8}>
                <LineChart 
                  title={'Revenue'}
                  keys={revenueByMonth !== {} ? Object.keys(revenueByMonth).reverse() : ['January', 'February', 'March', 'April', 'May', 'June']}
                  values={revenueByMonth !== {} ? Object.values(revenueByMonth).reverse() : [0,0,0,0,0,0]}                            
                  dataLabel={'Revenue'}
                  height={'40vh'}

                />
              </Grid>
              <Grid item xs={12} md={4}>
                <ROICard
                  total={totalRevenue} 
                  revenues={revenueByMonth}
                  height={'40vh'}
                  company = {userInfo.company}
                  monthsActive={monthsActive}
                />
                {/* <StateRevenueDonut /> */}
              </Grid>
            </>
          )}
          
          
          <Grid item xs={12} md={6}>
            <Stack spacing={-10} direction="column" alignItems="center">
              {/* Your Speedometer component */}
              <Speedometer
                title={'Customer Retention'}
                needleValue={allClients ? allClientCustomerRetention : revClientCustomerRetention}
              />
              <Stack spacing={0} direction="column" alignItems="center">
                {/* Typography component */}
                <Typography variant="h1" gutterBottom>
                  {allClients ? allClientCustomerRetention : revClientCustomerRetention}%
                </Typography>
                {/* Stack for Buttons */}
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Tooltip title="All Clients in Your Database">
                    <Button onClick={() => setAllClients(true)} variant={allClients ? 'contained' : 'outlined'}>
                      All Clients
                    </Button>
                  </Tooltip>
                  <Tooltip title="Clients With an Invoice">
                    <Button onClick={() => setAllClients(false)} variant={!allClients ? 'contained' : 'outlined'}>
                      Existing Clients
                    </Button>
                  </Tooltip>
                </Stack>
              </Stack>
            </Stack>
          </Grid>
          <Grid item xs={12} md={6}>
            <BarChart
              title={'Lead Data'}
              keys={recentlySoldByMonth !== {} ? Object.keys(recentlySoldByMonth).reverse() : ['January', 'February', 'March', 'April', 'May', 'June']}
              values1={recentlySoldByMonth === {} ? Object.values(recentlySoldByMonth).reverse() : [98, 43, 12, 32, 76, 33]}              
              dataLabel1={'Recently Moved'}
              values2={forSaleByMonth === {} ? Object.values(forSaleByMonth).reverse() : [25,15,76,45,22,88]}
              dataLabel2={'Customer Moving'}
            />
          </Grid>
        </Grid>
      </Container>
    </Page>
  );
}
