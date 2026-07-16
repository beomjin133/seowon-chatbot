const SearchIcon = ({
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
        d="M22 20L19.1212 17.1667M19.1212 10.9333C19.1212 15.3148 15.5124 18.8667 11.0606 18.8667C6.60886 18.8667 3 15.3148 3 10.9333C3 6.55187 6.60886 3 11.0606 3C15.5124 3 19.1212 6.55187 19.1212 10.9333Z"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default SearchIcon;
