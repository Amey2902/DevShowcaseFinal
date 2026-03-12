import { useAuth } from '@clerk/clerk-react';
import { useMemo } from 'react';
import { createApiClient } from '../utils/api';

export const useApi = () => {
  const { getToken } = useAuth();
  
  const api = useMemo(() => {
    return createApiClient(getToken);
  }, [getToken]);
  
  return api;
};
