import React, {useEffect, useState} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Dialog, DialogTitle, DialogContent, Divider, Stack, Tooltip } from "@mui/material"

import { selectClients } from '../redux/actions/usersActions';
import { upgradePlan } from '../redux/actions/authActions';

const UpgradeFromFree = () => {

    const listClient = useSelector(selectClients);
    const { count } = listClient;
    const [link, setLink] = useState("#");
    const [planName, setPlanName] = useState("Small Business");
    const [open, setOpen] = useState(true);
    const [monthlyOpen, setMonthlyOpen] = useState(false);
    const [annualOpen, setAnnualOpen] = useState(false);
    const [monthlyPrice, setMonthlyPrice] = useState("10");
    const [annualPrice, setAnnualPrice] = useState("100");
    const dispatch = useDispatch();

    useEffect(() => {
        if (count < 5000) {
            setLink("#");
            setPlanName("Small Business");
            setMonthlyPrice("150");
            setAnnualPrice("1,650");
        } else if (count < 10000) {
            setLink("#");
            setPlanName("Franchise");
            setMonthlyPrice("250");
            setAnnualPrice("2750");
        } else if (count < 20000) {
            setLink("#");
            setPlanName("Large Business");
            setMonthlyPrice("400");
            setAnnualPrice("4,400");
        } else {
            setLink("https://www.ismycustomermoving.com/#contact");
            setPlanName("Enterprise");            
        }
    }, [count]);

    const handleUpgradePlan = (period) => () => {
        setOpen(false);
        if (period === "month") {
            setMonthlyOpen(true);
        } else {
            setAnnualOpen(true);
        }
    }

    const handleConfirmMonth = () => {
        dispatch(upgradePlan("month"));
        setMonthlyOpen(false);
    }
    const handleConfirmAnnual = () => {
        dispatch(upgradePlan("year"));
        setAnnualOpen(false);
    }

    return (
        <>
            <Tooltip title="Upgrade to Premium to get all features" arrow>                
                <Button variant="contained" color="primary" onClick={()=>setOpen(!open)}>
                    Upgrade to Premium
                </Button>                                
            </Tooltip>
            <Dialog open={open} onClose={() => setOpen(false)}>
                <DialogTitle>Upgrade to a Premium Plan</DialogTitle>
                <Divider />
                <DialogContent>
                    <p style={{marginBottom: "16px"}}>
                        For <strong>{count}</strong> clients, you will need the <strong>{planName}</strong> plan.
                    </p>
                    { planName !== "Enterprise" ? (
                        <>
                            <p style={{marginBottom: "24px"}}>
                            This costs only <strong>${monthlyPrice}/month</strong><br/>Get <strong>10% off</strong> by paying annually for <strong>${annualPrice}/year</strong>.
                            </p>
                            <Stack direction="row" spacing={8}>
                                <Button variant="contained" color="error" onClick={()=>setOpen(false)}>Dismiss</Button>
                                <Stack direction="row" spacing={1}>
                                    <Button variant="contained" color="primary" onClick={handleUpgradePlan("month")}>Upgrade Monthly</Button>
                                    <Button variant="contained" color="primary" onClick={handleUpgradePlan("year")}>Upgrade Annually</Button>
                                </Stack>
                            </Stack>
                        </>
                    ):(
                        <div>
                            <p>This plan requires a special consultation. Book a meeting with the team below to get set up!</p>
                            <iframe
                                title='JB Setup Meeting'
                                src="https://letsmeet.io/jonathanbrewster/ismycustomermoving-demo"
                                // style="border:none; min-height: 700px; width: 1px; min-width: 100%; *width: 100%;"
                                style={{
                                border: "none",
                                minHeight: "700px",
                                // width: "1px",
                                minWidth: "100%",
                                width: "100%",
                                }}
                                name="booking"
                                scrolling="no"
                                frameBorder="0"
                                width="100%"
                                height="100%"
                                referrerPolicy="unsafe-url"
                                allowFullScreen
                            />
                        </div>
                    )}
                    
                </DialogContent>
            </Dialog>
            <Dialog open={monthlyOpen} onClose={() => setMonthlyOpen(false)}>
                <DialogTitle>Upgrade to a Premium Plan</DialogTitle>
                <Divider />
                <DialogContent>
                    <p style={{marginBottom: "16px"}}>
                        You have selected the monthly option. This will cost <strong>${monthlyPrice}/month</strong>.
                    </p>
                    <p style={{marginBottom: "24px"}}>
                        By confirming below, you acknowledge that you will be charged <strong>${monthlyPrice}/month</strong> on the card you have on file until you cancel your subscription.
                    </p>
                    <p>
                        You are also agreeing to both our <a href="https://app.ismycustomermoving.com/termsofservice" target="_blank" rel="noreferrer">Terms of Service</a> and <a href="https://app.ismycustomermoving.com/privacypolicy" target="_blank" rel="noreferrer">Privacy Policy</a>.
                    </p>
                    <Stack direction="row" spacing={8}>
                        <Button variant="contained" color="error" onClick={()=>setMonthlyOpen(false)}>Dismiss</Button>
                        <Button variant="contained" color="primary" onClick={handleConfirmMonth}>Confirm</Button>
                    </Stack>
                </DialogContent>
            </Dialog>
            <Dialog open={annualOpen} onClose={() => setAnnualOpen(false)}>
                <DialogTitle>Upgrade to a Premium Plan</DialogTitle>
                <Divider />
                <DialogContent>
                    <p style={{marginBottom: "16px"}}>
                        You have selected the annual option. This will cost <strong>${annualPrice}/month</strong>.
                    </p>
                    <p style={{marginBottom: "24px"}}>
                        By confirming below, you acknowledge that you will be charged <strong>${annualPrice}/year</strong> on the card you have on file until you cancel your subscription.
                    </p>
                    <p>
                        You are also agreeing to both our <a href="https://app.ismycustomermoving.com/termsofservice" target="_blank" rel="noreferrer">Terms of Service</a> and <a href="https://app.ismycustomermoving.com/privacypolicy" target="_blank" rel="noreferrer">Privacy Policy</a>.
                    </p>
                    <Stack direction="row" spacing={8}>
                        <Button variant="contained" color="error" onClick={()=>setAnnualOpen(false)}>Dismiss</Button>
                        <Button variant="contained" color="primary" onClick={handleConfirmAnnual}>Confirm</Button>
                    </Stack>
                </DialogContent>
            </Dialog>

        </>

    );
}

export default UpgradeFromFree;