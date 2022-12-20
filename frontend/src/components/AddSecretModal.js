import React, {useState} from 'react';
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
import { useDispatch } from 'react-redux';

import { companyAsync } from '../redux/actions/authActions';
import Iconify from './Iconify';

AddSecretModal.propTypes = {
    userInfo: Object
}


export default function AddSecretModal({userInfo}) {
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
        clientID: Yup.string("The Client ID is a string that should start with 'cid.'").required('Service Titan Client ID is required'),
        clientSecret: Yup.string("The Client Secret is a long string that is only generated one time").required('Service Titan Client Secret is required'),
    });

    const formik = useFormik({
        initialValues: {
        clientID: "",
        clientSecret: "",
        },
        validationSchema: IntegrateSTSchema,
        onSubmit: () => {
            console.log("values", values)
            setOpen(false);
            dispatch(companyAsync(userInfo, "", "", "", values.clientID, values.clientSecret))
        },
    });

    const { errors, touched, values, handleSubmit, getFieldProps } = formik;
  return (
    <div>
        <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
            Add Service Titan Client ID and Secret
        </Button>
        <IconButton onClick={()=>setIntegrateInfo(true)} >
            <Iconify icon="bi:question-circle-fill" />
        </IconButton>
        <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
            <DialogTitle>Service Titan Client ID and Secret</DialogTitle>
            <FormikProvider value={formik}>
                <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                    <Stack spacing={3}>
                        <TextField
                            fullWidth
                            label="Client ID"
                            placeholder="1234567890"
                            {...getFieldProps('clientID')}
                            error={Boolean(touched.clientID && errors.clientID)}
                            helperText={touched.clientID && errors.clientID}
                        />
                        <TextField
                            fullWidth
                            label="Client Secret"
                            placeholder="qwertyuiop"
                            {...getFieldProps('clientSecret')}
                            error={Boolean(touched.clientSecret && errors.clientSecret)}
                            helperText={touched.clientSecret && errors.clientSecret}
                        />
                    </Stack>
                </Form>
            </FormikProvider>
            <Stack direction="row" justifyContent="right">
                <Button color="error" onClick={handleClose}>Cancel</Button>
                <Button onClick={handleSubmit }>Submit</Button>
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
                    1. Now that you have submitted your Tenant ID, we will add your ID to our Application and send an email to notify you that it has been completed. <br/><br/>
                    2. You will then need to enable the IMCM application in your Service Titan account by going to Settings {'>'} Integrations {'>'} API Application Process. <br/><br/>
                    3. At this point, you will see the Client ID and Client Secret in your Service Titan account. <br/><br/>
                    4. Submit those here and then you will be able to use IMCM with your Service Titan account. <br/>
                    </Typography>                    
                </Box>
                </Fade>
            </Modal>
    </div>
  );
}