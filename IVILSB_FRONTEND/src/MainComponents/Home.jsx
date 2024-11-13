// Home.jsx
import React, { useState, useEffect } from "react";
import { BiPlay, BiPause, BiStop, BiSkipPrevious } from "react-icons/bi";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Local imports
import { enqueueAnimation, playQueue, pauseQueue, stopQueue, clearQueue, useQueueStatus } from "../Utils/Queue";
import { getFacefromArms, processText } from "../APIComponents/API";
import { databasePath, getDeviceType } from "../Utils/Config";
import Controller from "./Controller";
import "../Styles/Home.css";

const Home = () => {
  const [queueStatus, setQueueStatus] = useState('stopped'); // Add queue status state
  const [deviceType, setDeviceType] = useState(getDeviceType(window.innerWidth, window.innerHeight));
  const [inputText, setInputText] = useState("");
  const [processedText, setProcessedText] = useState("");

  useQueueStatus(setQueueStatus); // Use the custom hook to update queue status

  // Button class based on queue status
  const getButtonClass = (baseClass) => {
    if (queueStatus === 'empty') {
      return `${baseClass} almost-disabled`;
    } else if (queueStatus === 'stopped') {
      return `${baseClass} disabled`;
    } else {
      return baseClass;
    }
  };

  useEffect(() => {
    const handleResize = () => {
      setDeviceType(getDeviceType(window.innerWidth, window.innerHeight));
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleTextChange = (e) => {
    setInputText(e.target.value);
  };

  const handleLoadText = async () => {
    clearQueue(); // Clear the queue before adding new animations
    const loadingToast = toast.loading("Procesando texto...");
    let preProcessedText = inputText.replace(/[\n\r\t]+/g, " ");
    try {
      const response = await processText(preProcessedText);
      toast.update(loadingToast, { render: "Texto procesado!", type: "success", isLoading: false, autoClose: 3000 });
      console.log("Response:", response.data);
      if (response.data.ok) {
        setProcessedText(response.data.processed_text);
        for (const animationName of response.data.processed_text) {
          const faceName = await getFacefromArms(animationName, databasePath);
          enqueueAnimation({ arms: animationName, face: faceName });
        }
      } else {
        toast.error("Error processing text in Backend");
      }
    } catch (error) {
      toast.update(loadingToast, { render: "Error sending text to backend", type: "error", isLoading: false, autoClose: 3000 });
      console.error("Error:", error);
    }
  };

  const restartQueue = async () => {
    console.log("---------- [RESTART] ----------");
    clearQueue();
    for (const animationName of processedText) {
      const faceName = await getFacefromArms(animationName, databasePath);
      enqueueAnimation({ arms: animationName, face: faceName });
    }
    playQueue();
  }

  return (
    <div className={`home ${deviceType}`}>
      <div className="header">
        <p className="logo">IVILSB</p>
        <p className="title">Intérprete de Texto a Lengua de Señas Boliviano</p>
      </div>
      <div className="home-container">
        <div className="left-pane">
          <textarea
            placeholder="Escriba o pegue su texto aquí..."
            className="text-area"
            value={inputText}
            onChange={handleTextChange}
          />
          <div className="button-container">
            <button className={getButtonClass("left-button cargar-texto")} onClick={handleLoadText}>Cargar Texto</button>
            <button className={getButtonClass("left-button control-button")} onClick={playQueue}><BiPlay /></button>
            <button className={getButtonClass("left-button control-button")} onClick={pauseQueue}><BiPause /></button>
            <button className={getButtonClass("left-button restart")} onClick={restartQueue}><BiSkipPrevious /></button>
            <button className={getButtonClass("left-button stop")} onClick={stopQueue}><BiStop /></button>
          </div>
        </div>
        <div className="right-pane">
          <Controller />
        </div>
      </div>
      <ToastContainer />
    </div>
  );
};

export default Home;