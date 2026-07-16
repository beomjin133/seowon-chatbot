import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { loginApi } from "../authApi";

export const login = createAsyncThunk(
    "auth/login",
    async (credentials, { rejectWithValue }) => {
        try {
            const { token } = await loginApi(credentials);
            localStorage.setItem("token", token);
            return token;
        } catch (err) {
            // 에러 응답이 있는 경우
            if (err.response) {
                const status = err.response.status;
                const message = err.response.data?.message;

                // 401: 인증 실패 (이메일/비밀번호 불일치)
                if (status === 401) {
                    return rejectWithValue(
                        message || "이메일 또는 비밀번호가 일치하지 않습니다."
                    );
                }

                // 400: 잘못된 요청
                if (status === 400) {
                    return rejectWithValue(
                        message || "입력 정보를 확인해주세요."
                    );
                }

                // 500: 서버 오류
                if (status >= 500) {
                    return rejectWithValue(
                        "서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
                    );
                }

                // 기타 에러
                return rejectWithValue(
                    message || "로그인에 실패했습니다."
                );
            }

            // 네트워크 에러 (서버 응답 없음)
            if (err.request) {
                return rejectWithValue(
                    "네트워크 연결을 확인해주세요."
                );
            }

            // 기타 에러
            return rejectWithValue(
                "알 수 없는 오류가 발생했습니다."
            );
        }
    }
);

const loginSlice = createSlice({
    name: "login",
    initialState: {
        token: localStorage.getItem("token") || null,
        isLoggedIn: !!localStorage.getItem("token"),
        loading: false,
        error: "",
    },
    reducers: {
        logout: (state) => {
            localStorage.removeItem("token");
            state.token = null;
            state.isLoggedIn = false;
        },
        clearError: (state) => {
            state.error = "";
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(login.pending, (state) => {
                state.loading = true;
                state.error = "";
            })
            .addCase(login.fulfilled, (state, action) => {
                state.token = action.payload;
                state.isLoggedIn = true;
                state.loading = false;
                state.error = "";
            })
            .addCase(login.rejected, (state, action) => {
                state.error = action.payload;
                state.loading = false;
                state.isLoggedIn = false;
                state.token = null;
            });
    },
});

export const { logout, clearError } = loginSlice.actions;
export default loginSlice.reducer;