import {
  ListIcon,
  MailIcon,
  UserInfoIcon,
  CheckIcon,
  NextStepIcon,
} from "@/assets/icons/Icons";
import styles from "./RegisterStep.module.css"

const RegisterStep = ({ currentStep }) => {
  const stepIcons = [ListIcon, MailIcon, UserInfoIcon, CheckIcon];
  const stepLabels = ["약관동의", "이메일인증", "회원정보", "가입완료"];

  return (
    <div className={styles["step-wrap"]}>
      <ul className={styles["step-list"]}>
        {stepIcons.map((Icon, idx) => (
          <>
            <li
              key={idx}
              className={
                idx === currentStep
                  ? `${styles["step-group"]} ${styles["active"]}`
                  : styles["step-group"]
              }
            >
              <Icon
                color={
                  idx === currentStep
                    ? "var(--ico-color-primary)"
                    : "var(--ico-color-default)"
                }
              />
              <div className={styles["step-text"]}>
                <p>{stepLabels[idx]}</p>
              </div>
            </li>
            {idx < stepIcons.length - 1 && <NextStepIcon />}
          </>
        ))}
      </ul>
    </div>
  );
};

export default RegisterStep;
