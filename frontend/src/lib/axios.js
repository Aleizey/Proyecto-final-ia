import Axios from 'axios';

// cuanto tenga login
const getToken = () => localStorage.getItem("auth_token");

const axios = Axios.create({
    baseURL: import.meta.env.VITE_APP_BACKEND_URL,
    withCredentials: false,
    headers: {
        "Accept": "application/json",
        Authorization: `Bearer ${getToken()}`
    },
});

export default axios;