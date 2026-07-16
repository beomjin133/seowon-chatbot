import { useState, useEffect } from "react";
import styles from "../../../pages/RegisterPage.module.css";
import { emailSendApi, emailVerifyApi } from "@/modules/auth/authApi";

const StepEmail = ({ onNext }) => {
    const [email, setEmail] = useState("");
    const [authCode, setAuthCode] = useState("");
    const [requested, setRequested] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);
    const [isSending, setIsSending] = useState(false); // 이메일 전송 중 상태
    const [isVerifying, setIsVerifying] = useState(false); // 인증 확인 중 상태

    // 이메일은 공백이 아니면 OK
    const isEmailValid = email.trim() !== "";

    // 서버로 인증번호 요청할 최소 조건:
    // - 요청됨
    // - 제한시간 남아있음
    // - 4자리 숫자 입력됨
    const isAuthValid = requested && timeLeft > 0 && authCode.length === 4;

    const handleRequestAuth = async () => {
        if (!isEmailValid || isSending) return;

        setIsSending(true);
        try {
            await emailSendApi(email);
            setRequested(true);
            setTimeLeft(300); // 5분
            setAuthCode(""); // 기존 인증번호 초기화
            alert("인증번호가 이메일로 전송되었습니다.");
        } catch (err) {
            console.error(err);
            alert("인증 요청 중 오류가 발생했습니다.");
        } finally {
            setIsSending(false);
        }
    };

    const handleVerify = async (e) => {
        e.preventDefault();
        if (!isAuthValid || isVerifying) return;

        setIsVerifying(true);
        try {
            const result = await emailVerifyApi(email, authCode);

            if (result.status === "success") {
                alert("이메일 인증에 성공했습니다.");
                // 인증된 이메일을 다음 단계로 전달
                onNext(email);
            } else {
                alert("인증번호가 올바르지 않습니다.");
            }
        } catch (err) {
            console.error(err);
            alert("인증 중 오류가 발생했습니다.");
        } finally {
            setIsVerifying(false);
        }
    };

    // 타이머 카운트 다운
    useEffect(() => {
        if (timeLeft <= 0) return;

        const timer = setInterval(() => {
            setTimeLeft((prev) => prev - 1);
        }, 1000);

        return () => clearInterval(timer);
    }, [timeLeft]);

    const formatTime = (seconds) => {
        const m = String(Math.floor(seconds / 60)).padStart(2, "0");
        const s = String(seconds % 60).padStart(2, "0");
        return `${m} : ${s}`;
    };

    return (
        <form className={styles["register-form"]} onSubmit={handleVerify}>
            <header className={styles["register-header"]}>
                <h1 className={styles["register-title"]}>이메일 인증</h1>
                <p className={styles["register-sub-title"]}>
                    계정 분실에 대비하여{" "}
                    <span className={styles["register-highlight"]}>이메일 주소</span>{" "}
                    인증이 필요합니다.
                </p>
            </header>

            <section className={styles["register-content"]}>
                {/* 이메일 입력 */}
                <div className={styles["form-group"]}>
                    <label htmlFor="email" className={styles["form-label"]}>
                        이메일
                    </label>
                    <div className={styles["form-inline"]}>
                        <div className={styles["form-inp-box"]}>
                            <input
                                type="email"
                                id="email"
                                placeholder="email@email.com"
                                className={styles["form-inp"]}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                disabled={requested && timeLeft > 0}
                            />
                        </div>
                        <button
                            type="button"
                            className={styles["form-btn"]}
                            disabled={!isEmailValid || isSending}
                            onClick={handleRequestAuth}
                        >
                            {isSending ? "전송 중..." : requested ? "재전송" : "인증요청"}
                        </button>
                    </div>
                </div>

                {/* 인증코드 입력 */}
                <div className={styles["form-group"]}>
                    <label htmlFor="auth-code" className={styles["form-label"]}>
                        인증번호(숫자 4자리)
                    </label>
                    <div className={styles["form-auth-box"]}>
                        <input
                            type="text"
                            id="auth-code"
                            className={styles["form-inp"]}
                            placeholder="0000"
                            value={authCode}
                            onChange={(e) => {
                                const value = e.target.value.replace(/[^0-9]/g, "");
                                if (value.length <= 4) {
                                    setAuthCode(value);
                                }
                            }}
                            disabled={!requested || timeLeft <= 0}
                            maxLength={4}
                        />
                        <div className={styles["form-timer"]}>
                            {requested ? (timeLeft > 0 ? formatTime(timeLeft) : "만료됨") : ""}
                        </div>
                    </div>
                </div>
            </section>

            <footer className={styles["register-footer"]}>
                <button
                    type="submit"
                    className={styles["form-next-btn"]}
                    disabled={!isAuthValid || isVerifying}
                >
                    {isVerifying ? "확인 중..." : "인증확인"}
                </button>
            </footer>
        </form>
    );
};

export default StepEmail;