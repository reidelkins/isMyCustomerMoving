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


function RemoveErrorFlagButton({clientId}) {
    const dispatch = useDispatch();
    const [open, setOpen] = useState(false);
    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    const handleConfirm = () => {
        dispatch(updateClientAsync(clientId, "", "", false, "", ""));
        setOpen(false);
    }
    
    return (
        <div>
            <Button variant="outlined" color="primary" fullWidth onClick={handleOpen}>
                Want To Remove The Error Flag
            </Button>
            <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
                <DialogTitle>Remove Error Flag</DialogTitle>
                <Divider />
                <DialogContent>
                    <Stack spacing={3}>
                        <Typography>The error flag was added to this client because someone concluded that the status (For Sale or Recently Sold) was incorrect.</Typography>
                        <Typography>The flag normally resets after 180 days but if you want to reset it early then press confirm below.</Typography>
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

export default RemoveErrorFlagButton