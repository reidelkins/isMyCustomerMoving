import React, {useEffect, useState} from 'react';
import * as Yup from 'yup';
import {
    Button,
    IconButton,
    TextField,
    Dialog,
    DialogTitle,
    Stack,
    Modal,
    Backdrop,
    Fade,
    Box,
    Typography
} from '@mui/material';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch, useSelector } from 'react-redux';

import Iconify from './Iconify';

import { updateCompany } from '../redux/actions/usersActions';


export default function IntegrateSTModal() {
    // const classes = useStyles();
    const [open, setOpen] = useState(false);
    const [integrateInfo, setIntegrateInfo] = useState(false);

    const dispatch = useDispatch();
    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };

    const IntegrateSTSchema = Yup.object().shape({
        tenantID: Yup.number("The Tenant ID is a string of just numbers").required('Service Titan Tenant ID is required'),
    });

    
    
    const formik = useFormik({
        initialValues: {
        tenantID: '',
        },
        validationSchema: IntegrateSTSchema,
        onSubmit: () => {
            setOpen(false);
            dispatch(updateCompany("", "", values.tenantID))
            // window.location.reload();
        },
    });

    const { errors, touched, values, handleSubmit, getFieldProps } = formik;
  return (
    <div>
        <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
            Add Service Titan Tenant ID
        </Button>
        <IconButton onClick={()=>setIntegrateInfo(true)} >
            <Iconify icon="bi:question-circle-fill" />
        </IconButton>
        <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
            <DialogTitle>Service Titan Tenant ID</DialogTitle>
            <FormikProvider value={formik}>
                <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                    <Stack spacing={3}>
                        <TextField
                            fullWidth
                            label=""
                            placeholder="998190247"
                            {...getFieldProps('tenantID')}
                            error={Boolean(touched.tenantID && errors.tenantID)}
                            helperText={touched.tenantID && errors.tenantID}
                        />
                    </Stack>
                </Form>
            </FormikProvider>
            <Stack direction="row" justifyContent="right">
                <Button color="error" onClick={handleClose}>Cancel</Button>
                <Button onClick={handleSubmit}>Submit</Button>
            </Stack>
        </Dialog>
        <Modal
                open={integrateInfo}
                onClose={()=>setIntegrateInfo(false)}
                closeAfterTransition
                BackdropComponent={Backdrop}
                BackdropProps={{
                timeout: 500,
                }}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
                padding='10'
            >
                <Fade in={integrateInfo}>
                <Box sx={{position:'absolute', top:'50%', left:'50%', transform:'translate(-50%, -50%)', width:400, bgcolor:'white', border:'2px solid #000', boxShadow: '24px', p:'4%'}}>
                    <Typography id="modal-modal-title" variant="h5" component="h2">
                    Integrate IMCM With Your Service Titan Account
                    </Typography>
                    <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                    1. The first step is to submit your Tenant ID. This can be found in your Service Titan account under Settings `{'>'}` Integrations `{'>'}` API Application Access. <br/><br/>
                    2. Once you submit your Tenant ID, we will add your ID to our Application and send an email to notify you that has been completed. <br/><br/>
                    3. You will then need to enable the IMCM application in your Service Titan account. <br/><br/>
                    4. At this point, you will see the Client ID and Client Secret in your Service Titan account. <br/><br/>
                    5. Submit those here and then you will be able to use IMCM with your Service Titan account. <br/>
                    </Typography>                    
                </Box>
                </Fade>
            </Modal>
    </div>
  );
}