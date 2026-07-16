const ListIcon = ({
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
      <rect
        xmlns="http://www.w3.org/2000/svg"
        x="2"
        y="4"
        width="20"
        height="16"
        rx="4"
        stroke={color}
        strokeWidth="2"
        stroke-miterlimit="10"
      />
      <path
        xmlns="http://www.w3.org/2000/svg"
        d="M22 7L14.1407 13.0036C12.9584 13.9068 11.0416 13.9068 9.85932 13.0036L2 7M3.20032 18.5L9.20032 12.5M21 18L14.8 12.5"
        stroke={color}
        strokeWidth="2"
      />
    </svg>
  );
};

export default ListIcon;
