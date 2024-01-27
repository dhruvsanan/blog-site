import axios from 'axios'
axios.defaults.baseURL='http://localhost:5000';

let alertShown = false;
axios.interceptors.response.use(
    response => {
      return response;
    },
    error => {
      if (error.response.status === 401 && !alertShown) {
        alert("Token has expired");
        alertShown = true;
      }
      if (error.response.status === 422 && !alertShown) {
        alert("Please Log in");
        alertShown = true;
      }
      return Promise.reject(error);
    }
  );
  