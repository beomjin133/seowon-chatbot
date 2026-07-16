const PlusIcon = ({
  size = 24,
  color = "var(--ico-color-default)",
  className = "",
}) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
    >
      <path
        xmlns="http://www.w3.org/2000/svg"
        d="M12 3V12M12 12V21M12 12H21M12 12H3"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default PlusIcon;
