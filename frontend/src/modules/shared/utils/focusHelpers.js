export const focusInput = (ref) => {
    if (ref?.current) {
      ref.current.focus();
    }
  };
  