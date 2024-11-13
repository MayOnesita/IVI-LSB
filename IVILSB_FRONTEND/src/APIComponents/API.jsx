// API.jsx
import axios from "axios";
// Local imports
import { databasePath, defaultFace } from "../Utils/Config";

export const processText = async (text) => {
  try {
    const words = await fetchWordsfromJSON(databasePath);
    const response = await axios.post("http://localhost:8000/process_text", { text: text, words: words });
    return response;
  } catch (error) {
    console.error("Error sending text to backend:", error);
    throw error;
  }
};

const fetchWordsfromJSON = async (json_path) => {
  const words = [];
  try {
    const response = await fetch(json_path);
    const jsonData = await response.json();
    for (const val of jsonData) {
      words.push(val.arms);
    }
  } catch (error) {
    console.error("Error loading JSON data:", error);
  }
  return words;
};

export const getFacefromArms = async (arms, json_path) => {
  if (arms === "IDLE"){
    return defaultFace;
  }
  try {
    const response = await fetch(json_path);
    const jsonData = await response.json();
    for (const val of jsonData) {
      if (val.arms === arms) {
        return val.face;
      }
    }
    console.error(`[API] Face not found: ${arms}`);
    return defaultFace;
  } catch (error) {
    console.error("Error fetching or parsing JSON data:", error);
    return defaultFace;
  }
};