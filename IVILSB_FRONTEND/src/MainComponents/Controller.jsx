// Controller.jsx
import React, { useState, useEffect, useRef } from "react";

// Local imports
import Scene from "./Scene";
import { enqueueAnimation } from "../Utils/Queue";
import { databasePath, showButtons } from "../Utils/Config";
import "../Styles/Controller.css";

/*
FUNCTIONS:
- handleAnimationClick: Adds the animation to the queue when its button is clicked.
RENDER:
- The animation buttons and the 3D canvas.
*/
const Controller = () => {
  const [animations, setAnimations] = useState([]);
  const animationButtonsRef = useRef(null);

  // Fetch animations from the JSON database
  useEffect(() => {
    const fetchAnimations = async () => {
      try {
        const response = await fetch(databasePath);
        const data = await response.json();
        console.log("[JSON] Fetched Animations:", data);
        setAnimations(data);
      } catch (error) {
        console.error("Error fetching Animations:", error);
      }
    };
    fetchAnimations();
  }, []);

  // Custom scroll handler to reduce scroll sensitivity
  useEffect(() => {
    const handleWheel = (event) => {
      event.preventDefault();
      animationButtonsRef.current.scrollTop += event.deltaY * 0.2; // Adjust the multiplier to control sensitivity
    };

    const animationButtonsElement = animationButtonsRef.current;
    if (animationButtonsElement) {
      animationButtonsElement.addEventListener('wheel', handleWheel);
      return () => {
        animationButtonsElement.removeEventListener('wheel', handleWheel);
      };
    }
  }, []);

  // Add the animation to the queue when its button is clicked
  const handleAnimationClick = (animation) => {
    enqueueAnimation({ arms: animation.arms, face: animation.face });
  };

  // Render the animation buttons and the 3D canvas
  return (
    <div className="controller-container">
      <div className="canvas-container">
        <Scene />
        {showButtons && (
          <div className="animation-buttons" ref={animationButtonsRef}>
            {animations.map((anim, index) => (
              <button className="overlay-button" key={index} onClick={() => handleAnimationClick(anim)}>
                {anim.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}  

export default Controller;
