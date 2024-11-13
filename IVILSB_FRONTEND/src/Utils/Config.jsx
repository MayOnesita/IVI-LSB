// Config.jsx

// PATHS
export const databasePath = "/FBX/animations.json";
export const mainFBXPath = "/FBX/main.fbx";
export const avatarPath = "/FBX/main.glb";
export const facesPath = "/FBX/faces";

// DEFAULT
export const defaultArms = "IDLE";
export const defaultFace = "N";

// FLAGS
export const showAxes = false;
export const showButtons = false;

// Get the device type based on the screen width and height
export const getDeviceType = (width, height) => {
    const aspectRatio = width / height;
    if (aspectRatio < 0.6) return "phone";
    if (aspectRatio < 1.2) return "tablet"; 
    return "pc"; 
};

// Device settings for the 3D scene (FOV and camera position)
export const deviceSettings = {
    phone: { fov: 6, position: [0, -1.35, 0] },
    tablet: { fov: 5.5, position: [0, -1.35, 0] },
    pc: { fov: 6, position: [0, -1.35, 0] }
};

// Check if a file exists
export async function checkFileExists(filePath) {
    const fullPath = `${window.location.origin}/${filePath}`;
    try {
        const response = await fetch(fullPath);
        const contentType = response.headers.get("Content-Type");
        if (response.ok && !contentType.startsWith('text/html')) {
            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error('[Config] Error checking file existence:', error);
        return false;
    }
}
