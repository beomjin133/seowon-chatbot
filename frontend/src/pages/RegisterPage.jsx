import RegisterForm from "../components/register/layout/RegisterForm";
import styles from "./RegisterPage.module.css";

const RegisterPage = () => {
  return (
    <div className={styles["register-container"]}>
      <div className={styles["register-wrap"]}>
        <div className={styles["login-header"]}>
          <h1 className={styles["h-tit"]}>
            <span className="ico-logo logo-blue" />
          </h1>
        </div>
        <RegisterForm />
      </div>
    </div>
  );
};

export default RegisterPage;
