// Utils/FBX.jsx
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
import { mainFBXPath } from './Config';

// Load all FBX animations from the main FBX file
export const loadAllFBXAnimations = async () => {
  try {
    const fbx = await new FBXLoader().loadAsync(mainFBXPath);
    console.log('[FBX] Loaded Animations:', fbx.animations.map(anim => anim.name));
    return fbx.animations;
  } catch (error) {
    console.error('Error loading FBX:', error);
  }
};
