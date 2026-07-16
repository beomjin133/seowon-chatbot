import { useState } from "react";
import RegisterStep from "./RegisterStep";
import StepTerms from "../section/StepTerms";
import StepEmail from "../section/StepEmail";
import StepInfo from "../section/StepInfo";
import StepComplete from "../section/StepComplete";

const RegisterForm = () => {
    const [step, setStep] = useState(0); // 0 ~ 3
    const [verifiedEmail, setVerifiedEmail] = useState(""); // 인증된 이메일 저장

    // StepEmail에서 인증 완료 시 호출
    const handleEmailVerified = (email) => {
        console.log('이메일 인증 완료:', email);
        setVerifiedEmail(email); // 인증된 이메일 저장
        setStep(2); // 다음 단계로 이동
    };

    const renderStep = () => {
        switch (step) {
            case 0:
                return <StepTerms onNext={() => setStep(1)} />;
            case 1:
                return (
                    <StepEmail
                        onNext={handleEmailVerified}
                        onPrev={() => setStep(0)}
                    />
                );
            case 2:
                return (
                    <StepInfo
                        onNext={() => setStep(3)}
                        onPrev={() => setStep(1)}
                        verifiedEmail={verifiedEmail}
                    />
                );
            case 3:
                return <StepComplete />;
            default:
                return null;
        }
    };

    return (
        <>
            <RegisterStep currentStep={step} />
            {renderStep()}
        </>
    );
};

export default RegisterForm;