import { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { login, logout } from "./slices/loginSlice";
import { registerUser } from "./slices/registerSlice";
import { validateLogin } from "./authUtils";
import { focusInput } from "@/modules/shared/utils/focusHelpers";
import { resetChat, fetchRoomList } from "@/modules/chat/slices/chatSlice";
import { clearAllLocalStorage } from "@/modules/shared/utils/localStorage";

// ------------------------------- 로그인 -----------------------------------
export const useLogin = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { isLoggedIn, error } = useSelector((state) => state.login);

    const [email, setEmail] = useState("");
    const [user_password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = (e) => {
        e.preventDefault();
        setIsLoading(true);
        dispatch(login({ email, user_password })).then((res) => {
            if (res.meta.requestStatus === "fulfilled") {
                // ✅ 토큰이 반영된 다음에 fetchRoomList 실행
                setTimeout(() => {
                    const token = localStorage.getItem("token");
                    if (token) {
                        dispatch(fetchRoomList());
                    } else {
                        console.warn("⛔ 토큰이 아직 저장되지 않았음");
                    }
                }, 100); // 약간의 지연으로 token 반영 유도
            }
        });
    };

    useEffect(() => {
        if (isLoggedIn) {
            setIsLoading(false);
            navigate("/");
        } else if (error) {
            setIsLoading(false);
        }
    }, [isLoggedIn, error, navigate]);

    return {
        email,
        setEmail,
        user_password,
        setPassword,
        errorMessage: error,
        handleLogin,
        isLoading,
    };
};

// 로그인 폼 커스텀 훅
export const useLoginHandler = (email, user_password, handleLogin) => {
    const idRef = useRef(null);
    const passwordRef = useRef(null);
    const [localError, setLocalError] = useState("");

    const handleCustomLogin = (e) => {
        e.preventDefault();
        const result = validateLogin({ email, user_password });

        if (!result.ok) {
            if (result.focus === "email") focusInput(idRef);
            if (result.focus === "user_password") focusInput(passwordRef);

            setLocalError(result.message);
            return;
        }

        setLocalError("");
        handleLogin(e);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            handleCustomLogin(e);
        }
    };

    return {
        idRef,
        passwordRef,
        localError,
        handleCustomLogin,
        handleKeyDown,
    };
};

// ------------------------------- 회원가입 -----------------------------------
export const useRegister = (onSuccess, verifiedEmail = "") => {
    const dispatch = useDispatch();

    const [formData, setFormData] = useState({
        email: verifiedEmail, // 인증된 이메일로 초기화
        user_password: "",
        user_name: "",
    });
    const [passwordCheck, setPasswordCheck] = useState("");
    const [error, setError] = useState("");

    // verifiedEmail이 변경되면 formData에 반영
    useEffect(() => {
        if (verifiedEmail) {
            setFormData((prev) => ({ ...prev, email: verifiedEmail }));
        }
    }, [verifiedEmail]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.user_password !== passwordCheck) {
            setError("비밀번호가 일치하지 않습니다.");
            return;
        }

        try {
            await dispatch(registerUser(formData)).unwrap();
            onSuccess();
        } catch (err) {
            setError("회원가입에 실패했습니다.");
        }
    };

    return {
        formData,
        setFormData,
        passwordCheck,
        setPasswordCheck,
        handleSubmit,
        error,
    };
};

// ------------------------------- 로그아웃 -----------------------------------
export const useLogout = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleLogout = () => {
        clearAllLocalStorage();
        dispatch(resetChat());
        dispatch(logout());
        navigate("/");
    };

    return handleLogout;
};