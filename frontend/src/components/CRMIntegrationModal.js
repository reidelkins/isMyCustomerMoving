import React, {useEffect, useState} from "react";

import { Box, Grid, Dialog, DialogContent, DialogTitle, Divider, Button, Fade, Modal, Stack, TextField, Typography, IconButton } from "@mui/material";
import { useFormik, Form, FormikProvider } from 'formik';
import * as Yup from 'yup';
import { useDispatch, useSelector } from 'react-redux';
import PropTypes from 'prop-types';

import ServiceTitanTagsModal from './ServiceTitanTagsModal';
import AddSecretModal from './AddSecretModal';
import Iconify from './Iconify';

import { companyAsync, showSTInfo, salesForceAsync, salesForceTokenAsync } from '../redux/actions/authActions';

// prop validation
ServiceTitan.propTypes = {
    open: PropTypes.bool.isRequired,
    setOpen: PropTypes.func.isRequired,
    dispatch: PropTypes.func.isRequired,
}

// create a modal that shows different CRM options/buttons in a grid and has an input field for suggestions they don't see
// this modal will be shown when the user clicks on the CRM button in the header

// Dialog for Service Titan Integration
const ServiceTitan = ({open, setOpen, dispatch}) => {
    const [integrateInfo, setIntegrateInfo] = useState(false);
    const handleClose = () => {
        setOpen(false);
    }
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
            dispatch(companyAsync("", "", values.tenantID, "", "", "", "", "", "ServiceTitan"))
        },
    });

    const { errors, touched, values, handleSubmit, getFieldProps } = formik;
    return (
        <div>
            <Dialog open={open} onClose={handleClose} sx={{padding:"2px"}}>
                <DialogTitle>Service Titan</DialogTitle>
                <Divider />
                <DialogContent>
                    <p>To get started with Service Titan, submit your tenant ID.
                        <span>
                            <IconButton onClick={()=>setIntegrateInfo(true)} >
                                <Iconify icon="bi:question-circle-fill" />
                            </IconButton>
                        </span>
                    </p>
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
                </DialogContent>
            </Dialog>
            <Modal
                open={integrateInfo}
                onClose={()=>setIntegrateInfo(false)}
                closeAfterTransition               
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
    )
}

Salesforce.propTypes = {
    open: PropTypes.bool.isRequired,
    setOpen: PropTypes.func.isRequired,
}

// Dialog for Salesforce Integration
const Salesforce = ({open, setOpen}) => {
    const handleClose = () => {
        setOpen(false);
    }
    return (
        <div>
            <Dialog open={open} onClose={handleClose} sx={{margin:"12px"}}>
                <DialogTitle >Salesforce</DialogTitle>
            </Dialog>
        </div>
    )
}

const ComingSoon = () =>  (
    <div
        style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(255, 255, 255, 0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
        }}
        >
        <Typography variant="h6" color="textSecondary">
            Coming Soon
        </Typography>
    </div>
)


const Selected = () => (
    <div
        style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(255, 255, 255, 0.6)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
        }}
        >
        <Typography variant="h6" color="black">
            Selected
        </Typography>
    </div>
)


// // Dialog for Salesforce Integration
// const Hubspot = ({open, setOpen}) => {
//     const handleClose = () => {
//         setOpen(false);
//     }
//     return (
//         <div>
//             <Dialog open={open} onClose={handleClose} sx={{margin:"12px"}}>
//                 <DialogTitle >Salesforce</DialogTitle>
//             </Dialog>
//         </div>
//     )
// }

// // Dialog for Salesforce Integration
// const Zoho = ({open, setOpen}) => {
//     const handleClose = () => {
//         setOpen(false);
//     }
//     return (
//         <div>
//             <Dialog open={open} onClose={handleClose} sx={{margin:"12px"}}>
//                 <DialogTitle >Salesforce</DialogTitle>
//             </Dialog>
//         </div>
//     )
// }


const CRMIntegrationModal = ({user}) => {
    const [open, setOpen] = useState(false);
    const [stOpen, setStOpen] = useState(false);
    const [sfOpen, setSfOpen] = useState(false);
    const [hsOpen, setHsOpen] = useState(false);
    const [zohoOpen, setZohoOpen] = useState(false);

    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(salesForceAsync())
    }, [dispatch])

    const salesForce = useSelector(showSTInfo);

    const handleOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };

    const crmSchema = Yup.object().shape({
        crm: Yup.string()
            .required("CRM is required")
    });

    const formik = useFormik({
    initialValues: {
        crm: "",
    },
    validationSchema: crmSchema,
    onSubmit: (values) => {
        // dispatch(sendSuggestion(values.crm));
        setOpen(false);
    },
    });

  const { errors, handleSubmit, getFieldProps } = formik;

  const CRMs = [
    { name: "ServiceTitan", icon: "/static/icons/servicetitan.svg" },
    { name: "Salesforce", icon: "/static/icons/salesforce.svg" },
    { name: "HubSpot", icon: "/static/icons/hubspot.svg" },
    { name: "Zoho", icon: "/static/icons/zoho.svg" },
    ];

    const handleLogoButtonClick = (name) => {
        if (name !== user.company.crm) {
            if (name === "ServiceTitan") {
                setOpen(false);            
                setStOpen(true);
            } else if (name === "Salesforce") {
                setOpen(false);
                window.location.href = `https://login.salesforce.com/services/oauth2/authorize?response_type=code+token&client_id=${salesForce.key}&redirect_uri=${window.location.href}&scope=full%20refresh_token%20offline_access`;
                
            } else if (name === "salesforce") {
                window.location.href = `https://login.salesforce.com/services/oauth2/authorize?response_type=code&client_id=${salesForce.key}&redirect_uri=${window.location.href}&scope=full%20refresh_token%20offline_access`;
            } else if (name === "HubSpot") {
                setHsOpen(true);
            } else if (name === "Zoho") {
                setZohoOpen(true);
            }
        } 
    };

    useEffect(async () => {
        if (window.location.href.includes("code")) {
            const code = window.location.href.split("code=")[1];
            // const config = {
            //     headers: {
            //         'Content-type': 'application/json',
            //     },
            // };
            // const resp = await axios.get(`https://login.salesforce.com/services/oauth2/token?grant_type=authorization_code&client_id=${salesForce.key}&client_secret=${salesForce.secret}&redirect_uri=${window.location.href}&code=${code}`, config)
            // console.log(resp.data)
            dispatch(salesForceTokenAsync(code));
        }
    }, [dispatch])


  return (
    <div >
        {user.company.crm === "ServiceTitan" && (
            <div style={{marginBottom:"5%"}}>
                <Typography variant="h6" color="textSecondary">
                    You've Chosen Service Titan
                </Typography>
                {(!user.company.clientID && user.company.tenantID) && <AddSecretModal />}
                {user.company.clientID && <ServiceTitanTagsModal userInfo={user}/>}
            </div>
        )
        }
        {user.company.crm === "Salesforce" && (
            
            <div style={{marginBottom:"5%"}}>
                <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={() => handleLogoButtonClick("salesforce")}>
                    {/* <div style={{ width: 72, height: 72 }}>
                        <img alt={`Salesforce logo`} src={crm.icon} style={{ width: "100%", height: "100%" }} />                                                              
                    </div> */}
                    Reauthorize Salesforce
                </Button>
            </div>
        
        )}

        <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
            {user.company.crm === "None" ? "Connect" : "Change"} Your CRM
        </Button>    
        <Dialog open={open} onClose={handleClose} sx={{margin:"12px"}}>
            <DialogTitle > {user.company.crm === "None" ? "Pick" : "Change"} Your CRM</DialogTitle>
            <Divider/>

            <DialogContent>
                <Grid container spacing={0}>
                {CRMs.map((crm) => (
                    <Grid item key={crm.name} xs={6} md={4}>
                        <Button variant="contained" fullWidth style={{ height: "80%", width: "80%"  }} onClick={() => handleLogoButtonClick(crm.name)}>
                            <div style={{ width: 72, height: 72 }}>
                                <img alt={`${crm.name} logo`} src={crm.icon} style={{ width: "100%", height: "100%" }} />
                                {crm.name === "Zoho" && zohoOpen && <ComingSoon />}
                                {crm.name === "HubSpot" && hsOpen  && <ComingSoon />}
                                {crm.name === user.company.crm && <Selected />}                                                              
                            </div>
                        </Button>
                    </Grid>
                ))}
                </Grid>
                <div style={{ padding: '20px', fontSize: '1.2rem' }}>
                    <p>Don't see your CRM? Suggest it here</p>
                    <FormikProvider value={formik} >
                        <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                            <Box style={{display:"flex", justifyContent: "space-around"}}>
                                <TextField
                                    label="Tell us your CRM"
                                    margin="normal"
                                    name="token"
                                    type="text"
                                    {...getFieldProps("token")}
                                    error={Boolean(errors.token)}
                                    helperText={errors.token}                            
                                />
                                <Button variant="contained" onClick={handleSubmit} style={{marginTop: '5%', marginBottom:"3%"}}>Submit</Button>
                            </Box>
                        </Form>
                    </FormikProvider>                        
                </div>
            </DialogContent>
        </Dialog>
        <ServiceTitan open={stOpen} setOpen={setStOpen} dispatch={dispatch} sx={{margin:"12px"}}/>
        <Salesforce open={sfOpen} setOpen={setSfOpen} sx={{margin:"12px"}}/>
        {/* <Hubspot open={hsOpen} setOpen={setHsOpen} sx={{margin:"12px"}}/>
        <Zoho open={zohoOpen} setOpen={setZohoOpen} sx={{margin:"12px"}}/> */}
    </div>
  );
}

CRMIntegrationModal.propTypes = {
    user: PropTypes.object,
};

export default CRMIntegrationModal;