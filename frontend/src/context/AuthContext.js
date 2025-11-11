import React, { createContext, useContext, useMemo, useState } from 'react';

const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = async ({ email }) => {
    // TODO: Replace with Supabase authentication.
    setUser({
      email,
      displayName: email?.split('@')[0] ?? 'Guest',
    });
  };

  const signup = async ({ fullName, email }) => {
    // TODO: Replace with Supabase sign-up flow.
    const displayName = fullName?.trim() || email?.split('@')[0] || 'New User';
    setUser({
      email,
      displayName,
    });
  };

  const logout = () => {
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      login,
      signup,
      logout,
      isAuthenticated: Boolean(user),
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};


