const SendIcon = ({
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
        d="M5.80952 11.5L3.90231 16.2561C3.09885 18.2597 2.69712 19.2615 3.19449 19.729C3.69186 20.1964 4.66682 19.7333 6.61673 18.807L18.1967 13.3066C19.8451 12.5236 20.6693 12.1321 20.6693 11.5C20.6693 10.8679 19.8451 10.4764 18.1967 9.69344L6.61674 4.19295C4.66682 3.26674 3.69186 2.80363 3.19449 3.27104C2.69712 3.73845 3.09885 4.74026 3.90231 6.74389L5.80952 11.5ZM5.80952 11.5L10.5714 11.5"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default SendIcon;
