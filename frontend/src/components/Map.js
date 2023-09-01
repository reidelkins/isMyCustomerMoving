/* eslint-disable prefer-arrow-callback */
import React, { useState, useMemo, useEffect } from 'react'
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import PropTypes from 'prop-types';
import { useDispatch } from 'react-redux';

import { updateClientAsync } from '../redux/actions/usersActions';
import ZipCodeCircle from './ZipCodeArea';

const mainMapCardStyle = {
  height: "80vh",
  width: "100%"
}

const serviceAreaMapCardStyle = {
  height: "40vh",
  width: "50%"
}

Map.propTypes = {
  clients: PropTypes.array,
  serviceAreas: PropTypes.array,
  mapCardStyle: PropTypes.string,
  mapCenter: PropTypes.object,
  zoomLevel: PropTypes.number,
};

function Map({ mapCardStyle, mapCenter, zoomLevel,  clients = [], serviceAreas = [] }) {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_API_KEY,
  })
  const center = useMemo(() => (mapCenter), [mapCenter]);  

 

  const dispatch = useDispatch();
  
  const [isOpen, setIsOpen] = useState(false);
  const [infoWindowData, setInfoWindowData] = useState();
  const [markers, setMarkers] = useState([]);
  const [circles, setCircles] = useState([]);
  const [doneGettingCoords, setDoneGettingCoords] = useState(false);  

  const handleMarkerClick = (id, lat, lng, address, city, state, zip, name, status) => {
    // mapRef?.panTo({ lat, lng });
    setInfoWindowData({ id, address, city, state, zip, name, status });
    setIsOpen(true);
  };

  const serviceAreaMapOptions = {
    fullscreenControl: false,
    mapTypeControl: false,    
    mapTypeId: "terrain",    
    streetViewControl: false,                
  };

  const mapOptions = {
    
  };

  const getCoordinates = async (zip) => {
    const response = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${zip}&key=${
        process.env.REACT_APP_GOOGLE_API_KEY
      }`)
      const data = await response.json();
  
    if (data.results[0]) {
      return data.results[0].geometry.location;
    }
    return null;
  };

  useEffect(() => {
    serviceAreas.forEach(async (serviceArea) => {
      const coordinateData = await getCoordinates(serviceArea);
      if (coordinateData) {
        setCircles((circles) => [...circles, { lat: coordinateData.lat, lng: coordinateData.lng }]);
      }
    });
    // wait for 1 seconds before setting doneGettingCoords to true
    setTimeout(() => {
      setDoneGettingCoords(true);
    }, 1000);
  }, [serviceAreas]);
      


  async function getLatLngFromAddress(id, address, city, state, zip) {
    const fullAddress = `${address}, ${city}, ${state} ${zip}`;
    if (!address || !city || !state || !zip) return { lat: 0, lng: 0 };

    const response = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(fullAddress)}&key=${
        process.env.REACT_APP_GOOGLE_API_KEY
      }`
    );
    const data = await response.json();

    if (data.results && data.results.length > 0) {
      const { lat, lng } = data.results[0].geometry.location;
      dispatch(updateClientAsync(id, '', '', '', lat, lng));
      return { latitude: lat, longitude: lng };
    }
    return { lat: 0, lng: 0 };
  }

  useEffect(() => {
    const getMarkers = async () => {
      const clientsWithStatus = clients.filter((client) => client.status !== 'No Change');
      // const clientsWithStatus = clients.slice(0, 100);
      const markers = await Promise.all(
        clientsWithStatus.map(async (client) => {
          let lat = 0; // initializing with default values
          let lng = 0; // initializing with default values
          if (!client.latitude || !client.longitude) {
            const { latitude, longitude } = await getLatLngFromAddress(
              client.id,
              client.address,
              client.city,
              client.state,
              client.zipCode
            );
            lat = latitude;
            lng = longitude;
            dispatch(updateClientAsync(client.id, '', '', '', lat, lng));
          } else {
            lat = client.latitude;
            lng = client.longitude;
          }

          return { ...client, lat, lng };
        })
      );
      setMarkers(markers);
    };
    getMarkers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const renderZipCodeCircle = () => {
    if (doneGettingCoords) {
      return <ZipCodeCircle coordinates={circles} />;
    }
    return <div />;
  };

  return isLoaded ? (
      <GoogleMap
        mapContainerStyle={mapCardStyle === 'main' ? mainMapCardStyle : serviceAreaMapCardStyle}
        center={circles.length !== 0 ? circles[0] : center}
        zoom={zoomLevel}
        // onLoad={onLoad}
        // onUnmount={onUnmount}
        options={mapCardStyle === "main" ? mapOptions : serviceAreaMapOptions}
      >
      { mapCardStyle === "main" ? (
            markers.map(
            ({ address, city, state, zip, name, status, lat, lng }, ind) =>
              lat !== 0 &&
              lng !== 0 && (
                <Marker
                  icon={
                    status === 'House Recently Sold (6)'
                      ? 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                      : 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
                  }
                  key={ind}
                  position={{ lat, lng }}
                  onClick={() => {
                    handleMarkerClick(ind, lat, lng, address, city, state, zip, name, status);
                  }}
                >
                  {isOpen && infoWindowData?.id === ind && (
                    <InfoWindow
                      onCloseClick={() => {
                        setIsOpen(false);
                      }}
                    >
                      <div>
                        <h2>{infoWindowData.name}</h2>
                        <h3>{infoWindowData.address}</h3>
                        <h3>
                          {infoWindowData.city}, {infoWindowData.state} {infoWindowData.zip}
                        </h3>
                      </div>
                    </InfoWindow>
                  )}
                </Marker>
              )
          )
          ):(
            renderZipCodeCircle()
          )}
      </GoogleMap>
  ) : <></>
}

export default React.memo(Map)
