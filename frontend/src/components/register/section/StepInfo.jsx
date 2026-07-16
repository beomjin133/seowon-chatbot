import { useRegister } from "@/modules/auth/authHooks";
import styles from "../../../pages/RegisterPage.module.css";

const StepInfo = ({ onNext, verifiedEmail }) => {
    const {
        formData,
        setFormData,
        passwordCheck,
        setPasswordCheck,
        handleSubmit,
        error,
    } = useRegister(onNext, verifiedEmail); // verifiedEmail 전달

    const handleChange = (e) => {
        const { id, value } = e.target;
        setFormData((prev) => ({ ...prev, [id]: value }));
    };

    // email을 제외한 필드들만 체크
    const isAllFilled =
        formData.user_name?.trim() !== "" &&
        formData.user_password?.trim() !== "" &&
        passwordCheck.trim() !== "";

    return (
        <form className={styles["register-form"]} onSubmit={handleSubmit}>
            <header className={styles["register-header"]}>
                <h1 className={styles["register-title"]}>회원정보</h1>
                <p className={styles["register-sub-title"]}>
                    회원님의 소중한 정보를 입력해주세요.
                </p>
            </header>

            <section className={styles["register-content"]}>
                {/* 이메일 (읽기 전용) */}
                <div className={styles["form-group"]}>
                    <label htmlFor="email" className={styles["form-label"]}>
                        이메일
                    </label>
                    <div className={styles["form-inline"]}>
                        <div className={styles["form-inp-box"]}>
                            <input
                                id="email"
                                type="email"
                                value={formData.email || ""}
                                className={styles["form-inp"]}
                                disabled
                            />
                        </div>
                    </div>
                </div>

                {/* 사용자 이름 */}
                <div className={styles["form-group"]}>
                    <label htmlFor="user_name" className={styles["form-label"]}>
                        사용자 이름
                    </label>
                    <div className={styles["form-inline"]}>
                        <div className={styles["form-inp-box"]}>
                            <input
                                id="user_name"
                                type="text"
                                value={formData.user_name || ""}
                                onChange={handleChange}
                                placeholder="이름을 입력해주세요"
                                className={styles["form-inp"]}
                            />
                        </div>
                    </div>
                </div>

                {/* 비밀번호 */}
                <div className={styles["form-group"]}>
                    <label htmlFor="user_password" className={styles["form-label"]}>
                        비밀번호
                    </label>
                    <div className={styles["form-inline"]}>
                        <div className={styles["form-inp-box"]}>
                            <input
                                id="user_password"
                                type="password"
                                value={formData.user_password || ""}
                                onChange={handleChange}
                                placeholder="비밀번호"
                                className={styles["form-inp"]}
                            />
                        </div>
                    </div>
                </div>

                {/* 비밀번호 확인 */}
                <div className={styles["form-group"]}>
                    <label htmlFor="passwordCheck" className={styles["form-label"]}>
                        비밀번호 확인
                    </label>
                    <div className={styles["form-inline"]}>
                        <div className={styles["form-inp-box"]}>
                            <input
                                id="passwordCheck"
                                type="password"
                                value={passwordCheck}
                                onChange={(e) => setPasswordCheck(e.target.value)}
                                placeholder="비밀번호 확인"
                                className={styles["form-inp"]}
                            />
                        </div>
                    </div>
                </div>

                {error && <p className={styles["error-message"]}>{error}</p>}
            </section>

            <footer className={styles["register-footer"]}>
                <button
                    type="submit"
                    className={styles["form-next-btn"]}
                    disabled={!isAllFilled}
                >
                    회원가입 완료
                </button>
            </footer>
        </form>
    );
};

export default StepInfo;