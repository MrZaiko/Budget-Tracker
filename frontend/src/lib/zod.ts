import { z } from 'zod';

export const decimalString = z
  .string()
  .regex(/^\d+(\.\d{1,6})?$/, 'Must be a valid number (up to 6 decimal places)');

export const optionalDecimalString = z
  .string()
  .regex(/^\d+(\.\d{1,6})?$/, 'Must be a valid number')
  .optional()
  .or(z.literal(''));

export const uuidString = z.string().uuid();

export { z };
