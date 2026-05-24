const Tooltip = ({ label, children }) => (
  <span className="tooltip-wrapper" data-tooltip={label}>
    {children}
  </span>
);

export default Tooltip;
