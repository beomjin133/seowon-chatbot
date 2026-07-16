const CheckBoxIcon = ({
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
      <circle
        xmlns="http://www.w3.org/2000/svg"
        cx="12"
        cy="12"
        r="9"
        stroke={color}
        strokeWidth="2"
      />
      <path
        xmlns="http://www.w3.org/2000/svg"
        d="M17 9L10.3571 15.3409C9.97072 15.7098 9.36261 15.7098 8.97619 15.3409L7 13.4545"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default CheckBoxIcon;
