import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem(ACCESS_TOKEN);
// });

export default api;
