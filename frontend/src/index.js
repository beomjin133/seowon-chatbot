import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import store from '@/modules/shared/store';
import AppRouter from '@/routes/AppRouter';
import '@/global.css';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
    <Provider store={store}>
      <AppRouter />
    </Provider>
);
