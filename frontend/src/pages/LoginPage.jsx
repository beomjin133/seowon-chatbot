import LoginForm from "../components/login/layout/LoginForm";
import styles from "./LoginPage.module.css";

const LoginPage = () => {
  return (
    <div className={styles["login-container"]}>
      <div className={styles["login-wrap"]}>
        <div className={styles["login-header"]}>
          <h1 className={styles["h-tit"]}>
            <span className="ico-logo logo-blue" />
          </h1>
        </div>
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage;
