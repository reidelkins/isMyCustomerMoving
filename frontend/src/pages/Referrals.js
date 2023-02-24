import React, {useState, useEffect} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Stack, Container } from '@mui/material';
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
    const [incoming, setIncoming] = useState(false);

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
        <Page title="Referrals">
            <Container maxWidth="xl">
                {userInfo ? <ReferralListCall /> : null}
                <ReferralsData refs={REFERRALLIST} company={userInfo.company.id} incoming={incoming} />
                <Stack direction="row" spacing={2}>
                    <Button sx={ incoming ? selectedButton : notSelectedButton } variant="contained" onClick={handleIncoming}>Incoming</Button>
                    <Button sx={ !incoming ? selectedButton : notSelectedButton } variant="contained" onClick={handleOutgoing}>Outgoing</Button>
                </Stack>
            </Container>
        </Page>
    )
}