## Intérprete Virtual de la Lengua de Señas Boliviana (IVILSB)

This project is a web page that allows users to write text in Spanish and have a virtual avatar to translate and interpret it into Bolivian Sign Language. 

---
### Context

Deaf individuals in Bolivia primarily communicate using Bolivian Sign Language (LSB from spanish: Lengua de Señas Boliviana), a visual-gestural language that differs significantly from spoken and written Spanish. However, access to written information in Spanish remains a daily challenge for many Deaf people, especially those who are prelingually Deaf and for whom Spanish is a second language. This difficulty is further compounded by the scarcity of assistive tools tailored to their linguistic, social, and educational contexts.

Existing sign language technologies—such as mobile apps or motion capture-based translators—are often designed for hearing users, focus on other national sign languages like ASL, or depend heavily on the manual input of expert interpreters. Few tools aim to support Deaf users in developing Spanish literacy through their first language.

This project addresses this gap by providing a scalable, educational, and culturally relevant solution that allows Deaf Bolivians to access and understand written Spanish autonomously, using a virtual interpreter that respects the grammar and structure of LSB.

---
### Description of the Project

This project implements a web-based virtual interpreter designed to translate written Spanish into LSB through a 3D animated avatar. The core innovation lies in its custom animation scripting language and compiler, which formalize LSB gestures using labeled hand positions and vector-based arm movements—removing the need for manual motion capture or recorded videos.

The system consists of three components:

BLENDER: A custom Blender plugin enables users to model and animate LSB signs using predefined poses and rotation vectors. It includes a GUI for pose editing, gesture testing, and automatic export of animation files in .fbx format.

BACK-END: A Python-based server connects to OpenAI’s GPT-4o model to convert Spanish input into simplified "guide text" that conforms to LSB grammar and vocabulary. The system uses an iterative verification loop to ensure only valid LSB words are used.

FRONT-END: A React-based web application renders the 3D avatar using Three.js and plays the appropriate sign animations based on the processed guide text. The interface is intuitive and mobile-friendly, with visual feedback and playback controls.

Although still a prototype, this system aims to demonstrate a possible path toward making written Spanish more accessible for Deaf Bolivians. The approach is meant to be adaptable and extendable, offering a foundation that future projects can refine, expand, and build upon with the help of broader collaboration and more comprehensive datasets.

---
### Source Code

The project is divided into three main sub-projects: BLENDER, BACK-END, and FRONT-END. The first one provides tools for creating the animations, while the other two are responsible for the web page functionality.

**Main Sub-Projects**

- [**BLENDER**](IVILSB_BLENDER/README.md)
- [**BACK-END**](IVILSB_BACKEND/README.md)
- [**FRONT-END**](IVILSB_FRONTEND/README.md)
