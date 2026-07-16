const LogoutIcon = ({
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
        d="M9.5 19.5H6.16667C5.72464 19.5 5.30072 19.3244 4.98816 19.0118C4.67559 18.6993 4.5 18.2754 4.5 17.8333V6.16667C4.5 5.72464 4.67559 5.30072 4.98816 4.98816C5.30072 4.67559 5.72464 4.5 6.16667 4.5H9.5"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M15.3333 16.1667L19.5 12L15.3333 7.83334"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M19.5 12H9.5"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default LogoutIcon;
