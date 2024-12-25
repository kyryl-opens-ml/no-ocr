import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { initializeAuth } from './stores/authStore';
import Navbar from './components/layout/Navbar';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { AuthGuard } from './components/auth/AuthGuard';
import CreateCase from './components/CreateCase';
import Cases from './components/Case';
import Search from './components/Search';
import About from './components/About';

export default function App() {
  useEffect(() => {
    initializeAuth();
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          
          {/* Public route with navigation */}
          <Route
            path="/about"
            element={
              <>
                <Navbar />
                <About />
              </>
            }
          />
          
          {/* Protected routes */}
          <Route
            element={
              <AuthGuard>
                <>
                  <Navbar />
                  <main>
                    <Routes>
                      <Route path="/create-case" element={<CreateCase />} />
                      <Route path="/cases" element={<Cases />} />
                      <Route path="/search" element={<Search />} />
                      <Route path="/" element={<Navigate to="/search" replace />} />
                    </Routes>
                  </main>
                </>
              </AuthGuard>
            }
          >
            <Route path="/create-case" element={<CreateCase />} />
            <Route path="/cases" element={<Cases />} />
            <Route path="/search" element={<Search />} />
            <Route path="/" element={<Navigate to="/search" replace />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}