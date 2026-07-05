"use client";

import {
  getRedirectResult,
  onAuthStateChanged,
  signInWithRedirect,
  signOut,
  type User,
} from "firebase/auth";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getFirebaseAuth, googleProvider } from "@/lib/firebase";

type AuthState = {
  user: User | null;
  loading: boolean;
  configured: boolean;
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const auth = getFirebaseAuth();
  const [loading, setLoading] = useState(() => Boolean(auth));

  useEffect(() => {
    if (!auth) {
      return;
    }
    void getRedirectResult(auth).catch(() => {
      setLoading(false);
    });
    return onAuthStateChanged(auth, (nextUser) => {
      setUser(nextUser);
      setLoading(false);
    });
  }, [auth]);

  const value = useMemo<AuthState>(
    () => ({
      user,
      loading,
      configured: Boolean(auth),
      signIn: async () => {
        if (!auth) return;
        await signInWithRedirect(auth, googleProvider);
      },
      signOut: async () => {
        if (!auth) return;
        await signOut(auth);
      },
      getIdToken: async () => user?.getIdToken() ?? null,
    }),
    [auth, loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
