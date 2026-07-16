import { Link } from "react-router-dom";
import { useLogin, useLoginHandler } from "@/modules/auth/authHooks";
import GoogleLogo from "@/assets/logo/GoogleLogo";
import styles from "./LoginForm.module.css";

const LoginForm = () => {
  const {
    email,
    setEmail,
    user_password,
    setPassword,
    errorMessage,
    handleLogin,
    isLoading,
  } = useLogin();

  const { idRef, passwordRef, localError, handleCustomLogin, handleKeyDown } =
    useLoginHandler(email, user_password, handleLogin);

  return (
    <form className={styles["login-form"]} onSubmit={handleCustomLogin}>
      <div className={styles["login-content"]}>
        <div className={styles["login-title"]}>
          <h2>로그인</h2>
        </div>
        <div className="login-group">
          <div className={styles["inp-group"]}>
            <input
              type="email"
              className={styles["inp-fd"]}
              id="useremail"
              placeholder=""
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={handleKeyDown}
              ref={idRef}
            />
            <label htmlFor="useremail" className={styles["inp-lb"]}>
              이메일
            </label>
          </div>

          <div className={styles["inp-group"]}>
            <input
              type="password"
              className={styles["inp-fd"]}
              id="passwd"
              placeholder=""
              value={user_password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              ref={passwordRef}
            />
            <label htmlFor="passwd" className={styles["inp-lb"]}>
              비밀번호
            </label>
          </div>

          {(localError || errorMessage) && (
            <p className={styles["error-message"]}>
              {localError || errorMessage}
            </p>
          )}

          <div className="help-text-wrap">
            <p className={styles["help-text"]}>
              <Link to="/auth/remember">아이디 및 비밀번호를 잊으셨나요?</Link>
            </p>
          </div>
        </div>
      </div>
      <div className="login-btn-wrap">
        <button
          type="submit"
          className={styles["login-btn"]}
          disabled={isLoading}
        >
          {isLoading ? <span className={styles.spinner}></span> : "로그인"}
        </button>
        <p className={styles["signup-text"]}>
          계정이 없으신가요? <Link to="/auth/register">회원가입</Link>
        </p>
      </div>

      <button type="button" className={styles["google-btn"]}>
        <GoogleLogo size="20" />
        <span className={styles["google-btn-name"]}>Google 계정으로 로그인</span>
      </button>
    </form>
  );
};

export default LoginForm;
