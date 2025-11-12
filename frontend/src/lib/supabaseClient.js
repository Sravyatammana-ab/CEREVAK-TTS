import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://vkquetdomznqrjhgxmgg.supabase.co';
const SUPABASE_ANON_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZrcXVldGRvbXpucXJqaGd4bWdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MzI4NDcsImV4cCI6MjA3ODQwODg0N30.rSaeynU4Z-59PaP82fFAFpLem0qGICI31pjegJlsrrY';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
});


