[Home](../README.md)

# IVILSB : Blender

This project contains multiple tools for the project. Mainly, it contains two subprojects:
- **BLENDER**: The blender plugin that allows to try poses, create poses and create the animations.
- **COMPILER**: Converts the animation script into a database that will be read by the plug-in to create the animations. 

### Description

##### **COMPILER**

Instead of animating manually each sign animation, we encode an animation by a sequence of key poses, and we define an animation script that allows to write the animations with flexibility and use loops and speed modifiers.

- **client.py**: Fetches the table containing all the data (LSB available words, animation scripts, pose names, etc.) from Google Sheets.
- **database.py**: Converts the animation script into a formatted text file that will be read y the compiler.
- **compiler.py**: Compiles the formatted text file into a JSON animation database that will be read by the plug-in to create the animations.
- **main.py**: Main file that runs the 3 previous files in order.

##### **BLENDER**
Because of the Blender limitations, all the source code has to fit in one file. These are the main sections:
- **External files loading**: 
    - The constants are fixed scaling values, bone names or other values that are used in the plug-in. 
    - The database is the compiled JSON file that contains all the animations. 
    - The hand poses are savec in external files and loaded in the plug-in too.
- **Scale Functions**: The rotation angles are scaled for better visibility and control over the natural movements.
- **Arm Pose Functions**: Functions that allow to test and set the arm poses of the avatar. There is multiple tools like copy/pasting the pose, resetting the pose, etc. The arm poses are represented as 6 vectors, 3 for each arm, that represent the rotation of the shoulder, elbow and wrist.
- **Hand Pose Functions**: Functions that allow to test and set the hand pose of the avatar from the list of loaded hand poses.
- **Animation Functions**: Functions that allow to create the animations from the database. The animations are created by interpolating the key poses and the speed modifiers from the animation database.
