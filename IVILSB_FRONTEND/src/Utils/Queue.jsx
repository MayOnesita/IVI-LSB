// Queue.jsx
import { useEffect } from "react";
import { defaultArms, defaultFace } from "./Config";

// Animation queue
let queue = [];
// Animation flag to track if an animation is currently playing
let isPlaying = false;
// Animation flag to track if the queue is paused
let isPaused = true;
// Function to notify the component of the queue status
let notifyQueueStatus = null;

/**
 * Add the animation to the queue.
 * @param {Object} animation - The animation object to enqueue.
 */
export const enqueueAnimation = (animation) => {
  queue.push(animation);
  notifyQueueStatus && notifyQueueStatus(queue.length > 0 ? 'not_empty' : 'empty');
  if (!isPlaying && !isPaused) {
    playNextAnimation();
  }
};

/**
 * Dispatch the animation to the scene.
 * @param {function} dispatch - Function to dispatch the animation.
 */
let dispatchAnimation = () => {};
export const setDispatchAnimation = (dispatch) => {
  dispatchAnimation = dispatch;
};

/**
 * Play the next animation in the queue when the current animation is finished.
 */
const playNextAnimation = () => {
  if (queue.length > 0 && !isPaused) {
    const nextAnimation = queue.shift();
    notifyQueueStatus && notifyQueueStatus(queue.length > 0 ? 'not_empty' : 'empty');
    // console.log("[SEND]", nextAnimation);
    isPlaying = true;
    dispatchAnimation(nextAnimation, () => {
      isPlaying = false;
      playNextAnimation();
    });
  } else if (queue.length === 0) {
    console.log("[QUEUE] Empty");
    notifyQueueStatus && notifyQueueStatus('empty');
    resetToDefaultPose();
  }
};

/**
 * Reset to the default pose after the queue is empty.
 */
const resetToDefaultPose = () => {
  console.log("[RESET] Playing default animation");
  dispatchAnimation({ arms: defaultArms, face: defaultFace }, () => {
    isPlaying = false;
  });
};

/**
 * Play the queue.
 */
export const playQueue = () => {
  if (isPaused) {
    console.log("---------- [PLAY] ----------");
    isPaused = false;
    if (!isPlaying) {
      playNextAnimation();
    }
  }
};

/**
 * Pause the queue.
 */
export const pauseQueue = () => {
  console.log("---------- [PAUSE] ----------");
  isPaused = true;
};

/**
 * Stop the queue and reset to the default pose.
 */
export const stopQueue = () => {
  console.log("---------- [STOP] ----------");
  queue = [];
  notifyQueueStatus && notifyQueueStatus('stopped');
  isPlaying = false;
  isPaused = true;
  resetToDefaultPose();
};

export const clearQueue = () => {
  queue = [];
  notifyQueueStatus && notifyQueueStatus('stopped');
  isPlaying = false;
  isPaused = true;
};

/**
 * Custom hook to use the queue status.
 * @param {function} setQueueStatus - Function to set the queue status.
 */
export const useQueueStatus = (setQueueStatus) => {
  useEffect(() => {
    notifyQueueStatus = setQueueStatus;
    return () => {
      notifyQueueStatus = null;
    };
  }, [setQueueStatus]);
};
