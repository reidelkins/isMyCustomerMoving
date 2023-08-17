import React from 'react';
import { CircleF } from '@react-google-maps/api';
import PropTypes from 'prop-types';

ZipCodeCircle.propTypes = {
  lat: PropTypes.number,
  lng: PropTypes.number,
};

class ZipCodeCircle extends React.Component {
  constructor(props) {
    super(props);

    // Generate random fill and stroke colors    
    
    this.circleOptions = {
    //   strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#000FF0",
      fillOpacity: 0.35,
      center: {
        lat: props.lat,
        lng: props.lng,
      },
      radius: 30000, // Adjust this radius as needed
      clickable: false,
      draggable: false,
      editable: false,
      visible: true,
      zIndex: 1,
    };
  }

  render() {
    return (
      <CircleF {...this.circleOptions} />
    );
  }
}

export default ZipCodeCircle;
