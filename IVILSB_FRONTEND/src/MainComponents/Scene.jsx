// Scene.jsx
import React, { useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, OrbitControls, PerspectiveCamera } from "@react-three/drei";

// Local imports
import { Avatar } from "./Avatar";
import { showAxes, deviceSettings, getDeviceType } from "../Utils/Config";

/*
RENDER:
- The 3D canvas with the avatar and the environment.
- The axes helper if showAxes is true.
*/
const Scene = () => {
  const [deviceType, setDeviceType] = useState(getDeviceType(window.innerWidth, window.innerHeight));
  const { fov, position } = deviceSettings[deviceType];

  useEffect(() => {
    const handleResize = () => {
      setDeviceType(getDeviceType(window.innerWidth, window.innerHeight));
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize
    );
  }
  , [deviceType]);

  return (
    <Canvas>
      <PerspectiveCamera makeDefault fov={fov} position={[0, -10, 5]} />
      <OrbitControls
        minAzimuthAngle={-Math.PI / 8}
        maxAzimuthAngle={Math.PI / 8}
        enableZoom={true}
        enablePan={false}
        minPolarAngle={Math.PI / 2}
        maxPolarAngle={Math.PI / 2}
      />
      <Environment preset="sunset" />
      <group position={position}>
        <Avatar />
        {showAxes && <axesHelper args={[0.5]} />}
      </group>
    </Canvas>
  );
};

export default Scene;
