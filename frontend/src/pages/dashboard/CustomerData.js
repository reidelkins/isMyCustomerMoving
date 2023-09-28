/* eslint-disable camelcase */
import React, { useState, useEffect } from 'react';
// material
import {
  Alert,
  IconButton,
  Collapse,
  Stack,
  Container,
  Typography,
} from '@mui/material';

import { useSelector } from 'react-redux';

// components
import Page from '../../components/Page';
import FileUploader from '../../components/FileUploader';

import CounterCard from '../../components/cards/CounterCard';
import TabComponent from '../../components/styled-components/tabs';
import CustomerData from '../../components/CustomerData';
import NewAddressData from '../../components/NewAddressData';

import ClientsListCall from '../../redux/calls/ClientsListCall';
import {
  selectClients,
} from '../../redux/actions/usersActions';
import { showLoginInfo } from '../../redux/actions/authActions';

import '../../theme/map.css';

export default function HomePage() {
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const listClient = useSelector(selectClients);
  const { loading, CLIENTLIST, forSale, recentlySold, count, message, deleted, customerDataFilters } = listClient;
  useEffect(() => {
    if (message) {
      setAlertOpen(true);
    }
  }, [message]);

  const [alertOpen, setAlertOpen] = useState(false);

  const [deletedAlertOpen, setDeletedAlertOpen] = useState(false);

  useEffect(() => {
    if (deleted > 0) {
      setDeletedAlertOpen(true);
    }
  }, [deleted]);

  const [selectedTab, setSelectedTab] = useState(0);
  const tabLabels = ['Current Customers', 'New Addresses'];
  const handleSelectedTabChange = (newSelectedTab) => {
    setSelectedTab(newSelectedTab);
  };


  return (
    <div>
      {userInfo && (
        <Page title="Customer Data" userInfo={userInfo}>
          <Container>
            {userInfo ? <ClientsListCall /> : null}            
            {userInfo && (
              <>
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                  <Typography variant="h4" gutterBottom>
                    Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
                    {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
                  </Typography>
                </Stack>
                <Stack direction="row" alignItems="center" justifyContent="center" mb={5}>
                  <Typography variant="h3" gutterBottom>
                    {userInfo.company.name}
                  </Typography>
                </Stack>
                <Stack direction="row" alignItems="center" justifyContent="space-around" mb={5} mx={10}>
                  <Stack direction="column" alignItems="center" justifyContent="center">
                    <CounterCard start={0} end={forSale.current} title="For Sale" />
                    <Typography variant="h6" gutterBottom mt={-3}>
                      {' '}
                      All Time: {forSale.total}
                    </Typography>
                  </Stack>

                  <Stack direction="column" alignItems="center" justifyContent="center">
                    <CounterCard start={0} end={recentlySold.current} title="Recently Sold" />
                    <Typography variant="h6" gutterBottom mt={-3}>
                      {' '}
                      All Time: {recentlySold.total}
                    </Typography>
                  </Stack>
                </Stack>
                
                
                
                <TabComponent selectedTab={selectedTab} setSelectedTab={handleSelectedTabChange} tabLabels={tabLabels}/>
                
                {selectedTab === 0 ? (
                  <CustomerData userInfo={userInfo} CLIENTLIST={CLIENTLIST} loading={loading} customerDataFilters={customerDataFilters} count={count}/>
                ) : (
                  <NewAddressData userInfo={userInfo} />                                    
                )}
                  
                <Collapse in={deletedAlertOpen}>
                  <Alert
                    action={
                      <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => {
                          setDeletedAlertOpen(false);
                        }}
                      >
                        X
                      </IconButton>
                    }
                    sx={{ mb: 2, mx: 'auto', width: '80%' }}
                    variant="filled"
                    severity="error"
                  >
                    You tried to upload {deleted} clients more than allowed for your subscription tier. If you would
                    like to upload more clients, please upgrade your subscription.
                  </Alert>
                </Collapse>                

                {userInfo.status === 'admin' && <FileUploader fileType="ClientFile"/>}

                <Collapse in={alertOpen}>
                  <Alert
                    action={
                      <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => {
                          setAlertOpen(false);
                        }}
                      >
                        X
                      </IconButton>
                    }
                    sx={{ mb: 2, mx: 'auto', width: '50%' }}
                    variant="filled"
                    severity="success"
                  >
                    {message}
                  </Alert>
                </Collapse>
              </>
            )}
          </Container>
        </Page>
      )}
    </div>
  );
}