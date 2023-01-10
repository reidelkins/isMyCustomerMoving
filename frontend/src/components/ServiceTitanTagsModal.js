import React, {useState} from 'react';
import PropTypes from "prop-types";
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

ServiceTitanTagsModal.propTypes = {
    userInfo: PropTypes.objectOf(PropTypes.any),
}


export default function ServiceTitanTagsModal({userInfo}) {
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
        forSale: Yup.string("'"),
        forRent: Yup.string(""),
        recentlySold: Yup.string(""),
        
    });

    const formik = useFormik({
        initialValues: {
        forSale: userInfo.company.serviceTitanForSaleTagID,
        forRent: userInfo.company.serviceTitanForRentTagID,
        recentlySold: userInfo.company.serviceTitanRecentlySoldTagID,
        },
        validationSchema: IntegrateSTSchema,
        onSubmit: () => {
            setOpen(false);
            dispatch(companyAsync("", "", "", "", "", values.forSale, values.forRent, values.recentlySold))
        },
    });

    const { errors, touched, values, handleSubmit, getFieldProps } = formik;
  return (
    <div>
        <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
            {(userInfo.company.serviceTitanForSaleTagID || userInfo.company.serviceTitanForRentTagID || userInfo.company.serviceTitanRecentlySoldTagID) ? "Edit" : "Add"} Service Titan Tag IDs
        </Button>
        <IconButton onClick={()=>setIntegrateInfo(true)} >
            <Iconify icon="bi:question-circle-fill" />
        </IconButton>
        <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
            <DialogTitle>Service Titan Tag IDs</DialogTitle>
            <FormikProvider value={formik}>
                <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                    <Stack spacing={3}>
                        <TextField
                            fullWidth
                            label="For Sale ID"
                            placeholder="1234567890"
                            {...getFieldProps('forSale')}
                            error={Boolean(touched.forSale && errors.forSale)}
                            helperText={touched.forSale && errors.forSale}
                        />
                        {/* <TextField
                            fullWidth
                            label="For Rent ID"
                            placeholder="1234567890"
                            {...getFieldProps('forRent')}
                            error={Boolean(touched.forRent && errors.forRent)}
                            helperText={touched.forRent && errors.forRent}
                        /> */}
                        <TextField
                            fullWidth
                            label="Recently Sold ID"
                            placeholder="1234567890"
                            {...getFieldProps('recentlySold')}
                            error={Boolean(touched.recentlySold && errors.recentlySold)}
                            helperText={touched.recentlySold && errors.recentlySold}
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
                        Add Service Titan Tag IDs Instructions
                    </Typography>
                    <Typography id="modal-modal-description" sx={{ mt: 2 }}>        
                    1. Adding Tag IDs will enable automatically updating your customer list on service titan with the information found from IMCM <br/><br/>
                    2. First to make a new tag, log in to service titan, go to settings, search for tag, and click tag types, then click add. <br/><br/>
                    3. Next choose a color, a name (like "For Sale or Home Listed"), then click save. <br/><br/>
                    4. You then need to scroll the list of tags to find the one you just made. Once found, click the edit button on the row of that tag. <br/><br/>
                    5. Copy the ID number from the URL. It will be a long number like 1234567890. <br/><br/><br/>
                    Note: You can make 3 different tags for this data or you can make one tag and use the same ID for all 3.<br/>
                    Click <a href="https://www.loom.com/share/523b171ab81e47f2a050e1b28704c30e" target="_blank" rel="noreferrer">here </a> to see a video walking through this process.
                    </Typography>                    
                </Box>
                </Fade>
            </Modal>
    </div>
  );
}