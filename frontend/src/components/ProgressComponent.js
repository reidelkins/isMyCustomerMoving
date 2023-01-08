import React from "react";
import { useDispatch } from "react-redux";
import useWebSocket, { ReadyState } from "react-use-websocket";

import { WS } from "../redux/constants";
import { updateProgress, dataProgress } from "../redux/actions/usersActions";

// React component that uses Redux to store progress update data
export default function ProgressComponent() {
    // const dispatch = useDispatch();

    // const handleOpen = () => {
    //     // Send a message to start the process when the websocket connection is opened
    //     websocket.send(JSON.stringify({
    //         type: 'start'
    //     }));
    // };

    // const handleMessage = (event) => {
    //     const data = JSON.parse(event.data);
    //     if (data.type === 'update') {
    //         // Dispatch the Redux action to store the progress update data
    //         dispatch(updateProgress(data.progress));
    //     }
    // };
    
    // const websocket = new WebSocket(`${WS}/ws/createCompany/`);
    // websocket.onmessage = handleMessage;
    // websocket.onopen = handleOpen;

    const { readyState } = useWebSocket("ws://127.0.0.1:8000/chats/", {
        onOpen: () => {
            console.log("Connected!");
        },
        onClose: () => {
            console.log("Disconnected!");
        },
        // New onMessage handler
        onMessage: (e) => {
            console.log(e);
        }
    });

    const connectionStatus = {
        [ReadyState.CONNECTING]: "Connecting",
        [ReadyState.OPEN]: "Open",
        [ReadyState.CLOSING]: "Closing",
        [ReadyState.CLOSED]: "Closed",
        [ReadyState.UNINSTANTIATED]: "Uninstantiated"
    }[readyState];
    console.log(connectionStatus);

    

    
    return (
        <div>
            <p>Progress: {connectionStatus}%</p>
        </div>
    );
    
}