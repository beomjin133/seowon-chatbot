// 로그인 폼 유효성 검사 함수
export const validateLogin = ({ email, user_password }) => {
  if (!email) {
    return {
      ok: false,
      message: "아이디를 입력해 주세요.",
      focus: "user_id",
    };
  }

  if (!user_password) {
    return {
      ok: false,
      message: "비밀번호를 입력해 주세요.",
      focus: "user_password",
    };
  }

  return { ok: true };
};
