import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

// TODO: Replace with your actual Firebase project configuration
const firebaseConfig = {
    apiKey: "AIzaSyDbBJNWhQRmAS5YMG2xn4_Ik_83vHYXudM",
    authDomain: "krafti-app-12345.firebaseapp.com",
    projectId: "krafti-app-12345",
    storageBucket: "krafti-app-12345.firebasestorage.app",
    messagingSenderId: "879091920145",
    appId: "1:879091920145:web:98ef5e0da585b2409c30b0",
    measurementId: "G-2BN5H07JY0"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
