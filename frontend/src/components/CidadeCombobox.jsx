import { useState, useRef, useEffect } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Command, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem } from '@/components/ui/command';
import { cn } from '@/lib/utils';
import { Check, ChevronsUpDown, Loader2 } from 'lucide-react';

const CidadeCombobox = ({
  cidades = [],
  value,
  onValueChange,
  loading = false,
  disabled = false,
  placeholder = 'Selecione a cidade',
  loadingText = 'Carregando...',
  emptyText = 'Nenhuma cidade encontrada',
  searchPlaceholder = 'Buscar cidade...',
  allOption = null,
  className,
  triggerClassName,
  'data-testid': testId,
}) => {
  const [open, setOpen] = useState(false);

  const displayValue = () => {
    if (loading) return loadingText;
    if (allOption && value === allOption.value) return allOption.label;
    if (value) return value;
    return placeholder;
  };

  const isPlaceholder = !value || (allOption && value === allOption.value && !value);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          role="combobox"
          aria-expanded={open}
          disabled={disabled || loading}
          data-testid={testId}
          className={cn(
            'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            !value || isPlaceholder ? 'text-muted-foreground' : '',
            triggerClassName
          )}
        >
          <span className="truncate">{displayValue()}</span>
          {loading ? (
            <Loader2 className="ml-2 h-4 w-4 shrink-0 animate-spin opacity-50" />
          ) : (
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          )}
        </button>
      </PopoverTrigger>
      <PopoverContent className={cn('w-[--radix-popover-trigger-width] p-0', className)} align="start">
        <Command>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>{emptyText}</CommandEmpty>
            <CommandGroup>
              {allOption && (
                <CommandItem
                  value={allOption.label}
                  onSelect={() => {
                    onValueChange(allOption.value);
                    setOpen(false);
                  }}
                >
                  <Check className={cn('mr-2 h-4 w-4', value === allOption.value ? 'opacity-100' : 'opacity-0')} />
                  {allOption.label}
                </CommandItem>
              )}
              {cidades.map((cidade) => (
                <CommandItem
                  key={cidade}
                  value={cidade}
                  onSelect={() => {
                    onValueChange(cidade);
                    setOpen(false);
                  }}
                >
                  <Check className={cn('mr-2 h-4 w-4', value === cidade ? 'opacity-100' : 'opacity-0')} />
                  {cidade}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

export default CidadeCombobox;
