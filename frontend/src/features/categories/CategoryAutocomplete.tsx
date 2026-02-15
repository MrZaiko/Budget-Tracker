import React from 'react';
import { Autocomplete, CircularProgress, TextField } from '@mui/material';
import { createFilterOptions } from '@mui/material/Autocomplete';
import { useCategories, useCreateCategory } from './useCategories';
import type { TransactionTypeFilter } from '@/types/category';

interface OptionType {
  id?: string;
  name: string;
  inputValue?: string; // present only on the synthetic "Create X" option
}

const filter = createFilterOptions<OptionType>();

interface Props {
  value: string | null;           // category id
  onChange: (id: string | null) => void;
  transactionType?: TransactionTypeFilter | 'both';
  label?: string;
  error?: boolean;
  size?: 'small' | 'medium';
  fullWidth?: boolean;
}

const CategoryAutocomplete: React.FC<Props> = ({
  value,
  onChange,
  transactionType,
  label = 'Category',
  error,
  size = 'medium',
  fullWidth = true,
}) => {
  const { data: categories = [], isLoading } = useCategories();
  const createMutation = useCreateCategory();

  const filtered = transactionType && transactionType !== 'both'
    ? categories.filter(
        (c) => c.transaction_type === 'both' || c.transaction_type === transactionType
      )
    : categories;

  const options: OptionType[] = filtered.map((c) => ({ id: c.id, name: c.name }));

  const selectedOption = value ? (options.find((o) => o.id === value) ?? null) : null;

  const handleChange = (_: React.SyntheticEvent, newValue: OptionType | string | null) => {
    if (!newValue) {
      onChange(null);
      return;
    }

    // freeSolo raw string (shouldn't normally happen, but guard it)
    if (typeof newValue === 'string') {
      const existing = filtered.find((c) => c.name.toLowerCase() === newValue.toLowerCase());
      if (existing) {
        onChange(existing.id);
      } else {
        createMutation.mutate(
          { name: newValue, transaction_type: transactionType === 'both' || !transactionType ? 'both' : transactionType },
          { onSuccess: (created) => onChange(created.id) }
        );
      }
      return;
    }

    // "Create X" synthetic option
    if (newValue.inputValue) {
      createMutation.mutate(
        {
          name: newValue.inputValue,
          transaction_type: transactionType === 'both' || !transactionType ? 'both' : transactionType,
        },
        { onSuccess: (created) => onChange(created.id) }
      );
      return;
    }

    onChange(newValue.id ?? null);
  };

  return (
    <Autocomplete<OptionType, false, false, true>
      value={selectedOption}
      onChange={handleChange}
      options={options}
      loading={isLoading || createMutation.isPending}
      freeSolo
      selectOnFocus
      clearOnBlur
      handleHomeEndKeys
      getOptionLabel={(option) =>
        typeof option === 'string' ? option : option.inputValue ?? option.name
      }
      filterOptions={(opts, params) => {
        const filtered2 = filter(opts, params);
        const inputValue = params.inputValue.trim();
        const alreadyExists = opts.some(
          (o) => o.name.toLowerCase() === inputValue.toLowerCase()
        );
        if (inputValue !== '' && !alreadyExists) {
          filtered2.push({ inputValue, name: `Create "${inputValue}"` });
        }
        return filtered2;
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          size={size}
          error={error}
          fullWidth={fullWidth}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {(isLoading || createMutation.isPending) && (
                  <CircularProgress color="inherit" size={16} />
                )}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
};

export default CategoryAutocomplete;
