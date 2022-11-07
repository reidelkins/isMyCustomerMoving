import React from 'react';
import {
    IconButton,
    Button,
    Fade,
    TextField,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Stack
} from '@mui/material';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch } from 'react-redux';

import Iconify from './Iconify';
import { updateNote, users } from '../redux/actions/usersActions';


export default function AnimatedModal({
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
            dispatch(updateNote(values.note, id));
            console.log(values.note)
            setOpen(false);
            setTimeout(() => {dispatch(users())}, 500);
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
        {/* <Fade in={open}>
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Subscribe</DialogTitle>
                <DialogContent>
                <DialogContentText>
                    To subscribe to this website, please enter your email address here. We
                    will send updates occasionally.
                </DialogContentText>
                <TextField
                    autoFocus
                    margin="dense"
                    id="name"
                    label="Email Address"
                    type="email"
                    fullWidth
                    variant="standard"
                />
                </DialogContent>
                <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button onClick={handleClose}>Subscribe</Button>
                </DialogActions>
            </Dialog>
        </Fade> */}
    </div>
  );
}