import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Stack,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import { useDispatch } from 'react-redux';

import { serviceTitanSync } from '../redux/actions/usersActions';

const CenteredList = styled.div`
  text-align: center;
`;

const StyledOl = styled.ol`
  display: inline-block;
  text-align: left;
  margin: 0;
  padding-inline-start: 4em;
`;

const StyledListItem = styled.li`
  margin-bottom: 1em;
`;

// ServiceTitanSyncModal.propTypes = {
//   serviceTitanCustomerSyncOption: PropTypes.string,
// };

export default function ServiceTitanSyncModal(serviceTitanCustomerSyncOption) {
  const [open, setOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState(
    serviceTitanCustomerSyncOption.serviceTitanCustomerSyncOption ?? 'option1'
  );

  const dispatch = useDispatch();
  const handleOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = () => {
    setOpen(false);
    dispatch(serviceTitanSync(selectedOption));
  };

  return (
    <div>
      <Button
        variant="contained"
        color="primary"
        aria-label="Sync With Service Titan"
        component="label"
        onClick={handleOpen}
      >
        Sync With Service Titan
      </Button>
      <Dialog open={open} onClose={handleClose} sx={{ padding: '2px', borderRadius: '15px', boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)' }} >
        <DialogTitle>Sync With Service Titan</DialogTitle>
        <Divider />
        <DialogContent>
          <Typography variant="body1" sx={{ paddingBottom: '10px' }}>
            By pressing sync below, you are about to pull your client list from Service Titan. Because different
            companies have different needs and concerns, we have three options for you to choose from:
            <CenteredList>
              <StyledOl>
                <StyledListItem>
                  Pull in the client's name and phone number (when available) in addition to their address{' '}
                </StyledListItem>
                <StyledListItem>Only pull in the client's name and address</StyledListItem>
                <StyledListItem>Only pull in the list of addresses</StyledListItem>
              </StyledOl>
            </CenteredList>
            We recommend option 1 as it allows you to solely use our dashboard to reach out to your clients but the
            choice is yours!
          </Typography>
          <RadioGroup
            aria-label="options"
            name="options"
            value={selectedOption}
            onChange={(e) => setSelectedOption(e.target.value)}
            row
          >
            <FormControlLabel value="option1" control={<Radio />} label="Option 1" />
            <FormControlLabel value="option2" control={<Radio />} label="Option 2" />
            <FormControlLabel value="option3" control={<Radio />} label="Option 3" />
          </RadioGroup>

          <Stack direction="row" justifyContent="right">
            <Button color="error" onClick={handleClose}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Submit</Button>
          </Stack>
        </DialogContent>
      </Dialog>
    </div>
  );
}
