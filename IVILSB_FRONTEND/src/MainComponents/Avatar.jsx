// Avatar.jsx
import React, { useRef, useEffect, useState } from "react"; 
import { useGLTF, Plane, useAnimations } from "@react-three/drei";
import { useFrame, useLoader } from "@react-three/fiber";
import { TextureLoader } from "three";
import * as THREE from 'three';

// Local imports
import { avatarPath, facesPath, defaultArms, defaultFace } from "../Utils/Config";
import { loadAllFBXAnimations } from "../Utils/FBX";
import { setDispatchAnimation } from "../Utils/Queue";

// Custom hook to manage face texture
const useFaceTexture = (faceName) => {
  const [faceTexturePath, setFaceTexturePath] = useState(`${facesPath}/${defaultFace}.png`);
  useEffect(() => {
    if (faceName) {
      setFaceTexturePath(`${facesPath}/${faceName}.png`);
    }
  }, [faceName]);
  return useLoader(TextureLoader, faceTexturePath);
};

/*
FUNCTIONS:
- playAnimation: Plays the specified animation.
- useFrame: Updates the face plane position and rotation.
RENDER:
- The avatar 3D model.
- The face plane with the face texture.
*/
export function Avatar() {
  const group = useRef();
  const facePlaneRef = useRef();
  const { nodes, materials } = useGLTF(avatarPath);
  const [fbxAnimations, setFbxAnimations] = useState([]);
  const [currentFace, setCurrentFace] = useState(null);
  const currentAction = useRef(null);
  const faceTexture = useFaceTexture(currentFace);

  // Load all FBX animations when the component mounts
  useEffect(() => {
    const loadAnimations = async () => {
      const animations = await loadAllFBXAnimations();
      setFbxAnimations(animations);
    };
    loadAnimations();
  }, []);

  // Initialize animations and mixer
  const { actions, mixer } = useAnimations(fbxAnimations, group);

  // Set the animation to play when the actions change
  useEffect(() => {
    if (actions) {
      setDispatchAnimation((animation, onFinish) => {
        setCurrentFace(animation.face || defaultFace);
        playAnimation(animation.arms || defaultArms, onFinish);
      }); 
    } // eslint-disable-next-line
  }, [actions]);
  
  // Play the animation
  const playAnimation = (animationName, onFinish) => {
    if (actions && animationName) {
      // Ensure the animation name has the "Armature|" prefix
      if (!animationName.startsWith("Armature|")) {
        animationName = `Armature|${animationName}`;
      }
      const action = actions[animationName];
      if (!action) {
        console.error("Animation action not found:", animationName);
        onFinish();
        return;
      }
      // Check if the same animation is being played
      if (currentAction.current && currentAction.current.getClip().name === animationName) {
        // Play the same animation without smoothing
        action.reset().play();
        action.setLoop(THREE.LoopOnce, 1);
        action.clampWhenFinished = true;
        const onAnimationFinished = (e) => {
          if (e.action === action) {
            // console.log("[STOP]", animationName);
            mixer.removeEventListener("finished", onAnimationFinished);
            onFinish();
          }
        };
        mixer.addEventListener("finished", onAnimationFinished);
        currentAction.current = action;
        return;
      }
      console.log("[PLAY]", animationName);
      if (currentAction.current) {
        currentAction.current.fadeOut(0.3);
      }
      action.reset().fadeIn(0.3).play();
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true;
      const onAnimationFinished = (e) => {
        if (e.action === action) {
          // console.log("[STOP]", animationName);
          mixer.removeEventListener("finished", onAnimationFinished);
          onFinish();
        }
      };
      mixer.addEventListener("finished", onAnimationFinished);
      currentAction.current = action;
    } else {
      console.warn("Actions or animation name not available", { actions, animationName });
      onFinish();
    }
  };
  

  // Update the face plane position and rotation to follow "StudioROBOT_Face" bone
  useFrame(() => {
    if (group.current && facePlaneRef.current) {
      const face = group.current.getObjectByName("StudioROBOT_Face");
      if (face) {
        const faceWorldPosition = new THREE.Vector3();
        const faceWorldQuaternion = new THREE.Quaternion();
        face.getWorldPosition(faceWorldPosition);
        facePlaneRef.current.position.copy(faceWorldPosition);
        facePlaneRef.current.position.y += 1.385;
        face.getWorldQuaternion(faceWorldQuaternion);
        facePlaneRef.current.rotation.copy(new THREE.Euler().setFromQuaternion(faceWorldQuaternion.normalize()));
      }
    }
  });

  // Render the avatar
  return (
    <group ref={group} dispose={null}>
      <group name="Scene">
        <group name="Armature" scale={0.01}>
          <primitive object={nodes.StudioROBOT_Hips} />
          <group name="STUDIOROBOT_GEO">
            <skinnedMesh name="Mesh" geometry={nodes.Mesh.geometry} material={materials.BodyLight} skeleton={nodes.Mesh.skeleton} />
            <skinnedMesh name="Mesh_1" geometry={nodes.Mesh_1.geometry} material={materials.Light} skeleton={nodes.Mesh_1.skeleton} />
            <skinnedMesh name="Mesh_2" geometry={nodes.Mesh_2.geometry} material={materials.DarkBody} skeleton={nodes.Mesh_2.skeleton} />
            <skinnedMesh name="Mesh_3" geometry={nodes.Mesh_3.geometry} material={materials.Screen} skeleton={nodes.Mesh_3.skeleton} />
            <skinnedMesh name="Mesh_4" geometry={nodes.Mesh_4.geometry} material={materials.finger_1} skeleton={nodes.Mesh_4.skeleton} />
            <skinnedMesh name="Mesh_5" geometry={nodes.Mesh_5.geometry} material={materials.finger_2} skeleton={nodes.Mesh_5.skeleton} />
            <skinnedMesh name="Mesh_6" geometry={nodes.Mesh_6.geometry} material={materials.finger_3} skeleton={nodes.Mesh_6.skeleton} />
            <skinnedMesh name="Mesh_7" geometry={nodes.Mesh_7.geometry} material={materials.finger_4} skeleton={nodes.Mesh_7.skeleton} />
            <skinnedMesh name="Mesh_8" geometry={nodes.Mesh_8.geometry} material={materials.finger_5} skeleton={nodes.Mesh_8.skeleton} />
          </group>
        </group>
      </group>
      <Plane ref={facePlaneRef} args={[0.15, 0.15]}>
        <meshBasicMaterial attach="material" map={faceTexture} transparent />
      </Plane>
    </group>
  );
}

useGLTF.preload(avatarPath);
