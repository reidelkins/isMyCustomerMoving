import React, { useEffect} from 'react';
import { Grid, Stack, Container, Typography } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';

import ClientsListCall from '../../redux/calls/ClientsListCall';
import { showLoginInfo } from '../../redux/actions/authActions';
import { companyDashboardData, getCompanyDashboardDataAsync, selectClients } from '../../redux/actions/usersActions';
import Page from '../../components/Page';
import BarChart from '../../components/charts/Bar';
// import { StateRevenueDonut } from '../../components/charts/Donut';
import LineChart from '../../components/charts/Line';
import DashboardData from '../../components/cards/DashboardData';
import ROICard from '../../components/cards/ROICard';

export default function Home() {
  const dispatch = useDispatch();

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  const dashboardData = useSelector(companyDashboardData);  
  const { retrieved, monthsActive, totalRevenue, revenueByMonth, forSaleByMonth, recentlySoldByMonth } = dashboardData;
  const clientInfo = useSelector(selectClients);
  const { forSale, recentlySold } = clientInfo;

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
            bottomText={`${Object.values(revenueByMonth)[0]} This Month`}
            color="#85bb65"
            icon="/static/icons/revenue.svg"
          />
          <DashboardData
            mainText={forSale.total+recentlySold.total}
            topText="Total Leads Found"
            bottomText={`${Object.values(recentlySoldByMonth)[0]+Object.values(forSaleByMonth)[0]} This Month`}
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
                  keys={revenueByMonth !== {} ? Object.keys(revenueByMonth) : ['January', 'February', 'March', 'April', 'May', 'June']}
                  values={revenueByMonth !== {} ? Object.values(revenueByMonth) : [0,0,0,0,0,0]}                            
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
            <BarChart
              title={'Recently Moved Customers'}
              keys={recentlySoldByMonth !== {} ? Object.keys(recentlySoldByMonth) : ['January', 'February', 'March', 'April', 'May', 'June']}
              values={recentlySoldByMonth !== {} ? Object.values(recentlySoldByMonth) : [0,0,0,0,0,0]}              
              dataLabel={'Recently Moved'}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <BarChart 
              title={'Customers Moving'}
              keys={forSaleByMonth !== {} ? Object.keys(forSaleByMonth) : ['January', 'February', 'March', 'April', 'May', 'June']}
              values={forSaleByMonth !== {} ? Object.values(forSaleByMonth) : [0,0,0,0,0,0]} 
              dataLabel={'Moving'} 
            />
          </Grid>
        </Grid>
      </Container>
    </Page>
  );
}
