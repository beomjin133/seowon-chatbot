import axios from "../shared/api/axiosInstance";

//서버에 POST방식으로 정보를 바디에 담아 보내고 비동기(async) 함수로 서버 응답을 기다림(await)
export const loginApi = async ({ email, user_password }) => {
  const response = await axios.post("/auth/login", {
    email,
    user_password,
  }); //baseURL + /auth/login = http://localhost:8080/api/auth/login로 post요청
  return response.data; //응답 객체에서 data만 꺼내서 함수를 호출한 쪽에 넘겨줌
};

//서버에 POST방식으로 data를 바디에 담아서 요청함
export const registerApi = async (formData) => {
  const response = await axios.post("/auth/register", formData);
  return response.data;
};

export const emailSendApi = async (email) => {
    const response = await axios.post("/email/send", {email})
    return response.data;
}

export const emailVerifyApi = async (email, code) => {
    const response = await axios.post("/email/verify", {
        email,
        code
    });
    return response.data;
};