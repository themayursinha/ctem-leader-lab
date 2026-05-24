import { Search as SearchIcon } from 'lucide-react';

const TableSearch = ({ value, onChange, placeholder = 'Search...' }) => (
  <div className="table-search-wrap">
    <SearchIcon size={16} className="table-search-icon" />
    <input
      className="table-search"
      type="text"
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      aria-label={placeholder}
    />
  </div>
);

export default TableSearch;
