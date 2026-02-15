import { useQuery } from '@tanstack/react-query';
import { getSubscriptions, getUpcomingSubscriptions } from '@/api/recurring';

export const useSubscriptions = () =>
  useQuery({ queryKey: ['subscriptions'], queryFn: getSubscriptions });

export const useUpcomingSubscriptions = (days = 30) =>
  useQuery({
    queryKey: ['subscriptions', 'upcoming', days],
    queryFn: () => getUpcomingSubscriptions(days),
  });
