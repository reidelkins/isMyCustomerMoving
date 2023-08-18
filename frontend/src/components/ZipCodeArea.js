import React from 'react';
import { Polygon, Circle } from '@react-google-maps/api';
import PropTypes from 'prop-types';
import getConvexHull from '../utils/getConvexHull';



class ZipCodeArea extends React.Component {
  constructor(props) {
    super(props);
    this.path = props.coordinates.length === 1 ? props.coordinates : getConvexHull(props.coordinates);
      
  }  

  render() {    

    
    return (
      this.path.length > 1 ? (
        <Polygon
          paths={this.path}
          options={{
            fillColor: `#ff00ff`,
            fillOpacity: 0.4,
            strokeColor: `#000000`,
            strokeWeight: 2,
            clickable: false,
            draggable: false,
            editable: false,
          }} 
        />
      ): (
        <Circle
          center={this.path[0]}
          options={{
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: "#000FF0",
            fillOpacity: 0.35,
            radius: 30000, // Adjust this radius as needed
            clickable: false,
            draggable: false,
            editable: false,
            visible: true,
            zIndex: 1
          }}
        />
      )
      
      
    );
  }
}

ZipCodeArea.propTypes = {
  coordinates: PropTypes.array.isRequired  
};

export default ZipCodeArea;
