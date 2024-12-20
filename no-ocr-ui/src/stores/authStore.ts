import { create } from 'zustand';
import { AuthState } from '../types/auth';
import { supabase } from '../config/supabase';

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
}));

// Initialize auth state
export const initializeAuth = async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    useAuthStore.setState({
      user: session?.user ?? null,
      isLoading: false,
    });

    // Set up auth state change listener
    supabase.auth.onAuthStateChange((_event, session) => {
      useAuthStore.setState({
        user: session?.user ?? null,
        isLoading: false,
      });
    });
  } catch (error) {
    console.error('Error initializing auth:', error);
    useAuthStore.setState({ isLoading: false });
  }
};