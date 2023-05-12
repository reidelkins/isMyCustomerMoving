import React, {useState} from 'react';
import {
    Button,
    Dialog,
    DialogTitle,
    Divider,
    DialogContent,
    Stack,
    Typography
} from '@mui/material';
import { useDispatch } from 'react-redux';

import { updateClientAsync } from '../redux/actions/usersActions';


function IncorrectDataButton({clientId}) {
    const dispatch = useDispatch();
    const [open, setOpen] = useState(false);
    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    const handleConfirm = () => {
        dispatch(updateClientAsync(clientId, "", "", true));
        setOpen(false);
    }
    
    return (
        <div>
            <Button variant="outlined" color="error" fullWidth onClick={handleOpen}>
                Error In Data?
            </Button>
            <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
                <DialogTitle>Wrong Housing Status?</DialogTitle>
                <Divider />
                <DialogContent>
                    <Stack spacing={3}>
                        <Typography>If this client's home has been incorrectly marked as for sale/recently sold, press confirm below.</Typography>
                        <Typography>Letting us know this fixes the status of the customer in your dashboard, removes any Is My Customer Moving tags for the customer in your CRM, and allows us to investigate the issue in order to get better for you!  </Typography>
                    </Stack>
                        
                    <Stack direction="row" justifyContent="space-between">                        
                        <Stack direction="row" justifyContent="right">
                            <Button color="error" onClick={handleClose}>Cancel</Button>
                            <Button onClick={handleConfirm }>Confirm</Button>
                        </Stack>
                    </Stack>
                </DialogContent>
            </Dialog>
        </div>
    )
}

export default IncorrectDataButton