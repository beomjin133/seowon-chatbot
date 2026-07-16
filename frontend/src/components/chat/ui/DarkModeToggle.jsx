import styles from './DarkModeToggle.module.css';

const DarkModeToggle = ({ isDarkMode, onToggle }) => {
  return (
    <button
      type="button"
      className={styles['toggle-container']}
      onClick={onToggle}
      aria-label={isDarkMode ? '라이트 모드로 전환' : '다크 모드로 전환'}
      aria-pressed={isDarkMode}
    >
      <div className={styles['toggle-track']}>
        <div
          className={`${styles['toggle-thumb']} ${
            isDarkMode ? styles['active'] : ''
          }`}
        >
          <span className={styles['toggle-icon']}>
            {isDarkMode ? '🌙' : '☀️'}
          </span>
        </div>
      </div>
    </button>
  );
};

export default DarkModeToggle;
