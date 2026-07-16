const CheckIcon = ({
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
        d="M19 6L8.70711 16.2929C8.31658 16.6834 7.68342 16.6834 7.29289 16.2929L4 13"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default CheckIcon;
