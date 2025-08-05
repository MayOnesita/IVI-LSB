[Home](../README.md)


## IVILSB : FRONTEND
This project contains the front-end code for the IVILSB Web Page.

### Description 
The front-end of the web page provides the user interface and manages the display of the 3D virtual interpreter that signs in Bolivian Sign Language (LSB).

The main responsibilities of the front-end are:

- User Input Interface: Allows users to enter Spanish text to be interpreted.

- Request Handling: Sends the input text to the back-end and receives the corresponding list of validated signs.

- 3D Rendering: Loads the 3D avatar and displays sign animations using Three.js, with support from @react-three-fiber and @react-three-drei.

- Facial Expressions: Dynamically updates the avatar’s face based on the instructions code of the signs.

- Animation Control: Provides play, pause, reset, and stop buttons for controlling the animation playback.

- Feedback & Logs: Displays status messages (e.g., processing, success, error) and shows debug information in the browser console for development purposes.

### Components Hierarchy

> **APIComponents**
>> API.jsx
>> JSON.jsx

> **MainComponents**
>> Avatar.jsx
>> Controller.jsx
>> Home.jsx
>> Scene.jsx

> **SharedComponents**
>> AnimationList.jsx

> **Utils**
>> Config.jsx
>> FBX.jsx

> **Styles**
>> Controller.css

> App.jsx
> index.js
> index.css


### Create Avatar model

To create an  Avatar component, run this script:
```bash
npx gltfjsx path\to\model.glb
```
