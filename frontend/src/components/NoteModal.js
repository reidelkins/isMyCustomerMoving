import React, {useEffect, useState} from 'react';
import {
    IconButton,
    Button,
    TextField,
    Dialog,
    DialogTitle,
    Stack
} from '@mui/material';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import { useAuth0 } from "@auth0/auth0-react";

import Iconify from './Iconify';
import { updateClientAsync } from '../redux/actions/usersActions';

NoteModal.propTypes = {
    passedNote: PropTypes.string,
    id: PropTypes.string,
    name: PropTypes.string,

}

export default function NoteModal({
  passedNote,
  id,
  name,

}) {
    const [open, setOpen] = useState(false);
    const dispatch = useDispatch();
    const { getAccessTokenSilently } = useAuth0();
    const [accessToken, setAccessToken] = useState(null);

    useEffect(() => {
    const fetchAccessToken = async () => {
        const token = await getAccessTokenSilently();
        setAccessToken(token);
    };

    fetchAccessToken();

    // return a cleanup function to cancel any pending async operation and prevent updating the state on an unmounted component
    return () => {
        setAccessToken(null);
    };
    }, [getAccessTokenSilently]);
    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        values.note = passedNote
        setOpen(false);
    };
    
    const formik = useFormik({
        initialValues: {
        note: passedNote,
        },
        onSubmit: () => {
            dispatch(updateClientAsync(id, "", values.note, accessToken));
            setOpen(false);
        },
    });

    const { values, handleSubmit, getFieldProps } = formik;
    return (
        <div>
            <IconButton color="primary" aria-label="View/Edit Note" component="label" onClick={handleOpen}>
                <Iconify icon="eva:edit-fill" />
            </IconButton>
            <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
                <DialogTitle>Note for {name}</DialogTitle>
                <FormikProvider value={formik}>
                    <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                        <Stack spacing={3}>
                        {passedNote ? (
                            <TextField
                            fullWidth
                            multiline
                            defaultValue={passedNote}
                            {...getFieldProps('note')}
                        />
                        ) : (
                            <TextField
                                fullWidth
                                multiline
                                defaultValue="Enter Note Here"
                                {...getFieldProps('note')}
                            />
                        )}                        
                        </Stack>
                    </Form>
                </FormikProvider>
                <Stack direction="row" justifyContent="right">
                    <Button color="error" onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleSubmit}>Submit</Button>
                </Stack>
            </Dialog>
        </div>
    );
}