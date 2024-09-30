const axios = require('axios');

axios.get(process.env.REACT_APP_BACKEND_URL).then(response => {console.log(response.data);}).catch(error => {console.error('Error fetching data:', error);});

axios.get('http://flask-backend:8080/').then(response => {console.log(response.data);}).catch(error => {console.error('Error fetching data:', error);});


const baseUrl = process.env.REACT_APP_BACKEND_URL  || '';
axios.get(`${baseUrl}`).then(response => {console.log(response.data);}).catch(error => {console.error('Error fetching data:', error);});

