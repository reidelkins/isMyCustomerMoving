import React, {useState} from 'react';
import { useSelector } from 'react-redux';
import { Button, Stack, Container, Box, Typography } from '@mui/material';
import { grey, orange } from '@mui/material/colors';

import { referralsAsync, selectReferrals } from '../redux/actions/usersActions';
import { showLoginInfo } from '../redux/actions/authActions';
import ReferralsData from '../components/ReferralsData';
import Page from '../components/Page';
import ReferralListCall from '../redux/calls/ReferralListCall';

// define style for button that is selected
const selectedButton = {
    bgcolor: orange[300],
    '&:hover': {
        bgcolor: orange[700],
    },
}
// define style for button that is not selected
const notSelectedButton = {
    bgcolor: grey[500],
    '&:hover': {
        bgcolor: grey[700],
    },
}



export default function Referrals() {
    const [incoming, setIncoming] = useState(true);

    const userLogin = useSelector(showLoginInfo);
    const { userInfo } = userLogin;

    const referrals = useSelector(selectReferrals);
    const { REFERRALLIST } = referrals;


    const handleIncoming = () => {
        setIncoming(true);
    }
    const handleOutgoing = () => {
        setIncoming(false);
    }

    return(
        <Page title="Referrals" userInfo={userInfo}>
            <Container maxWidth="xl">
                {userInfo.company.franchise ? (
                    <>
                        {userInfo ? <ReferralListCall /> : null}
                        <ReferralsData refs={REFERRALLIST} company={userInfo.company.id} incoming={incoming} />
                        <Stack direction="row" spacing={2}>
                            <Button sx={ incoming ? selectedButton : notSelectedButton } variant="contained" onClick={handleIncoming}>Incoming</Button>
                            <Button sx={ !incoming ? selectedButton : notSelectedButton } variant="contained" onClick={handleOutgoing}>Outgoing</Button>
                        </Stack>
                    </>
                )
                : (
                   // message that tells user they do not belong to a franchise and therefore cannot access this page
                   <Box
                    className="bg-gray-100 p-8 rounded-md shadow-md"
                    sx={{ maxWidth: 500, margin: '0 auto' }}
                    >
                    <Typography variant="h4" component="h1" gutterBottom>
                        Access Restricted
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                        We're sorry, but it appears that you do not have access to this page.
                        This page is reserved for companies who belong to a franchise that have an account.
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                        If you are interested in the benefits of being part of a franchise within Is My Customer Moving, contact us!
                    </Typography>
                    </Box>
                )}
                
            </Container>
        </Page>
    )
}