import { useState } from "react";
import { CheckBoxIcon } from "@/assets/icons/Icons";
import styles from "../../../pages/RegisterPage.module.css";

const StepTerms = ({ onNext }) => {
  const [checkedTerms, setCheckedTerms] = useState({
    "01": false,
    "02": false,
    "03": false,
    "04": false,
  });

  const toggleCheck = (id) => {
    setCheckedTerms((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const requiredIds = ["01", "02", "03"];
  const isRequiredChecked = requiredIds.every((id) => checkedTerms[id]);

  const isAllChecked = Object.values(checkedTerms).every((v) => v === true);

  return (
    <form
      className={styles["register-form"]}
      onSubmit={(e) => {
        e.preventDefault();
        onNext();
      }}
    >
      <header className={styles["register-header"]}>
        <h1 className={styles["register-title"]}>Chat-OS 회원 이용약관</h1>
        <p className={styles["register-sub-title"]}>
          Chat-OS 서비스이용을 위해 아래 이용약관 및 정보이용에 동의해주세요.
        </p>
      </header>

      <section className={styles["terms-section"]}>
        <div className={styles["terms-all"]}>
          <span className={styles["terms-all-label"]}>전체동의</span>
          <button
            type="button"
            className={styles["terms-check-all-btn"]}
            onClick={() => {
              const newValue = !isAllChecked;
              setCheckedTerms({
                "01": newValue,
                "02": newValue,
                "03": newValue,
                "04": newValue,
              });
            }}
          >
            <CheckBoxIcon
              size="28"
              color={
                isAllChecked
                  ? "var(--ico-color-primary)"
                  : "var(--ico-color-disabled)"
              }
            />
          </button>
        </div>

        <ul className={styles["terms-list"]}>
          {[
            { id: "01", label: "Chat-OS 서비스 이용 약관", required: true },
            {
              id: "02",
              label: "개인(신용)정보 수집 및 이용동의",
              required: true,
            },
            { id: "03", label: "개인정보 취급 동의", required: true },
            { id: "04", label: "마케팅 정보 수신 동의", required: false },
          ].map(({ id, label, required }) => (
            <li key={id} className={styles["terms-item"]}>
              <div className={styles["terms-text"]}>
                <span className={styles["terms-id"]}>{id}.</span>
                <p className={styles["terms-label"]}>{label}</p>
                <p
                  className={`${styles["terms-tag"]} ${
                    required ? styles["tag-red"] : ""
                  }`}
                >
                  ({required ? "필수" : "선택"})
                </p>
              </div>
              <button
                type="button"
                className={styles["terms-check-btn"]}
                onClick={() => toggleCheck(id)}
              >
                <CheckBoxIcon
                  color={
                    checkedTerms[id]
                      ? "var(--ico-color-primary)"
                      : "var(--ico-color-disabled)"
                  }
                />
              </button>
            </li>
          ))}
        </ul>
      </section>

      <footer className={styles["register-footer"]}>
        <button
          type="submit"
          className={styles["form-next-btn"]}
          disabled={!isRequiredChecked}
        >
          다음
        </button>
      </footer>
    </form>
  );
};

export default StepTerms;
