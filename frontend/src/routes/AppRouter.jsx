import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatPage from '@/pages/ChatPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';

const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      <Route path='/' element={<ChatPage />} />
      <Route path='/auth/login' element={<LoginPage />} />
      <Route path='/auth/register' element={<RegisterPage />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;
