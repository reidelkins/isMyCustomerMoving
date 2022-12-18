import React from 'react';
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

import Iconify from './Iconify';
import { updateClientAsync } from '../redux/actions/usersActions';


export default function NoteModal({
  passedNote,
  id,
  name,
}) {
    // const classes = useStyles();
    const [open, setOpen] = React.useState(false);
    const dispatch = useDispatch();
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
            dispatch(updateClientAsync(id, "", values.note));
            setOpen(false);
        },
    });

    const { errors, touched, values, isSubmitting, handleSubmit, getFieldProps } = formik;
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