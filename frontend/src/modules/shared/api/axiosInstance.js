import axios from 'axios';
const axiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api',
  withCredentials: true, //쿠키 인증 관련 설정임(true로 해줘야 제대로 전송)
  headers: {
    'Content-Type': 'application/json', //요청 시 데이터 타입(json)
  },
});

//Intercepor 설정(응답이 오가기 전, 중간에 가로채서 처리하는 함수)
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config; //토큰이 있을 경우 Authorization헤더에 추가하여 보냄, 없을 경우 추가하지 않음
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
