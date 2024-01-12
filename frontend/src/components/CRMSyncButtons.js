import {     
    Button, 
} from '@mui/material';
import { useDispatch } from 'react-redux';
import ServiceTitanSyncModal from './ServiceTitanSyncModal';
import { hubspotSync, salesForceSync } from '../redux/actions/usersActions';


const CRMSyncButtons = ({ userInfo }) => {
    const dispatch = useDispatch();
    const sfSync = () => {
      dispatch(salesForceSync());
    };
    const hsSync = () => {
      dispatch(hubspotSync());
    };
    const renderButton = () => {
        if (userInfo.company.crm === 'ServiceTitan') {
            return (
                <ServiceTitanSyncModal
                    serviceTitanCustomerSyncOption={userInfo.company.service_titan_customer_sync_option}
                />
            );
        }
        if (userInfo.company.crm === 'Salesforce') {
            return (
                <Button onClick={sfSync} variant="contained">
                    Sync With Salesforce
                </Button>
            );
        }
        if (userInfo.company.crm === 'HubSpot') {
            return (
                <Button onClick={hsSync} variant="contained">
                    Sync With Hubspot
                </Button>
            );
        }
        
    };

    return renderButton();
};

export default CRMSyncButtons;

