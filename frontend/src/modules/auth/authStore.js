import loginReducer from "./slices/loginSlice";
import registerReducer from "./slices/registerSlice";

const authReducers = {
  login: loginReducer, // 슬라이스를 하나의 객체로 묶음 추후 state.login과 같이 상태를 사용할 때 사용됨
  register: registerReducer,
};

export default authReducers;