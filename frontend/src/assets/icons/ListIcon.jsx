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
      <path
        xmlns="http://www.w3.org/2000/svg"
        d="M8 3V3C5.79086 3 4 4.79086 4 7V13C4 16.7712 4 18.6569 5.17157 19.8284C6.34315 21 8.22876 21 12 21V21C15.7712 21 17.6569 21 18.8284 19.8284C20 18.6569 20 16.7712 20 13V7C20 4.79086 18.2091 3 16 3V3"
        stroke={color}
        strokeWidth="2"
        stroke-miterlimit="10"
      />
      <rect
        xmlns="http://www.w3.org/2000/svg"
        x="8"
        y="2"
        width="8"
        height="3"
        rx="1"
        stroke={color}
        strokeWidth="2"
        stroke-miterlimit="10"
      />
    </svg>
  );
};

export default ListIcon;
