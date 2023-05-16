import React, { useState, useMemo, useEffect } from "react";
import { GoogleMap, Marker, useLoadScript, InfoWindow } from "@react-google-maps/api";
import { Card } from '@mui/material';


import "../theme/map.css"

export default function Map({clients}) {

    
    const [mapRef, setMapRef] = useState();
    const [isOpen, setIsOpen] = useState(false);
    const [infoWindowData, setInfoWindowData] = useState();
    const [markers, setMarkers] = useState([]);

    const { isLoaded } = useLoadScript({
        googleMapsApiKey: process.env.REACT_APP_GOOGLE_API_KEY,
    });
    const center = useMemo(() => ({ lat: 39.50, lng: -98.35 }), []);    


    const handleMarkerClick = (id, lat, lng, address, city, state, zip, name, status) => {
        mapRef?.panTo({ lat, lng });
        setInfoWindowData({ id, address, city, state, zip, name, status });
        setIsOpen(true);
    };

    async function getLatLngFromAddress(address, city, state, zip) {
        const fullAddress = `${address}, ${city}, ${state} ${zip}`;
        if (!address || !city || !state || !zip) return { lat: 0, lng: 0 };
        
        const response = await fetch(
            `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
            fullAddress
            )}&key=${process.env.REACT_APP_GOOGLE_API_KEY}`
        );
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            const { lat, lng } = data.results[0].geometry.location;
            return { lat, lng };
        }
        return { lat: 0, lng: 0 };                
    }

    useEffect(() => {
        const getMarkers = async () => {
            const clientsWithStatus = clients.filter(client => client.status !== 'No Change');
            // const clientsWithStatus = clients.slice(0, 100);
            const markers = await Promise.all(
            clientsWithStatus.map(async (client) => {
                    const { lat, lng } = await getLatLngFromAddress(client.address, client.city, client.state, client.zipCode);                                      
                    return { ...client, lat, lng };
                    
                })
            );
            setMarkers(markers);
        };
        getMarkers();
    }, []);

    return (
        <Card style={{width: "100%", height: "80vh"}}>
            {!isLoaded ? (
                <h1>Loading...</h1>
            ) : (
                
                <GoogleMap
                    mapContainerClassName="map-container"
                    center={center}
                    zoom={4.5}
                >
                    {markers.map(({ address, city, state, zip, name, status, lat, lng }, ind) => (
                        lat !== 0 && lng !== 0 && (
                            <Marker
                                icon= {status === "House Recently Sold (6)" ? "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" : "http://maps.google.com/mapfiles/ms/icons/red-dot.png"}
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
                                        <h3>{infoWindowData.city}, {infoWindowData.state} {infoWindowData.zip}</h3>
                                    </div>
                                </InfoWindow>
                                )}
                            </Marker>
                    )
                    
                    ))}
                </GoogleMap>
                
            )}
        </Card>
    )
}