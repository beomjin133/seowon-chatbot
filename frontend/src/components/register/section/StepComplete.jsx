import { useNavigate } from "react-router-dom";
import { CheckIcon } from "@/assets/icons/Icons";
import styles from "../../../pages/RegisterPage.module.css";

const StepComplete = () => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate("/");
  };

  const handleGoLogin = () => {
    navigate("/auth/login");
  };
  return (
    <form className={styles["register-form"]}>
      <header className={styles["register-header"]}>
        <div>
          <CheckIcon size="100" color="var(--ico-color-primary)" />
        </div>
        <h1 className={styles["register-title"]}>
          회원가입이 <span className={styles["register-highlight"]}>완료</span>{" "}
          되었습니다.
        </h1>
        <p className={styles["register-sub-title"]}>
          회원님의 가입을 축하합니다! 좋은 서비스로 찾아뵙겠습니다.
        </p>
      </header>
      <div className={styles["divider"]} />
      <footer className={styles["register-footer"]}>
        <button
          type="button"
          className={styles["form-home-btn"]}
          onClick={handleGoHome}
        >
          홈으로
        </button>
        <button
          type="button"
          className={styles["form-login-btn"]}
          onClick={handleGoLogin}
        >
          로그인
        </button>
      </footer>
    </form>
  );
};

export default StepComplete;
