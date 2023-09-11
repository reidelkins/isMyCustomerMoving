import {
    Grid,
    Tooltip
} from '@mui/material';

const GridSetting = ({
    label,
    value,
    tooltip
}) => {
    return (
        
        <Tooltip title={tooltip} >
            <Grid item xs={12} md={4}>
                <h3>{label}</h3>
                <p>{value}</p>            
            </Grid>
        </Tooltip>
    )
}

export default GridSetting;
