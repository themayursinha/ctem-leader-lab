import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

const stageMap = {
  '/': 'Dashboard',
  '/scoping': 'Scoping',
  '/discovery': 'Discovery',
  '/prioritization': 'Prioritization',
  '/validation': 'Validation',
  '/mobilization': 'Mobilization',
  '/workshop-pack': 'Workshop Pack',
  '/sessions': 'Sessions',
  '/guide': 'User Guide',
};

const Breadcrumbs = ({ pathname }) => {
  const crumbs = [];
  if (pathname !== '/') {
    crumbs.push({ label: 'Home', to: '/' });
  }
  const label = stageMap[pathname];
  if (label) {
    crumbs.push({ label, to: pathname });
  }

  if (crumbs.length <= 1) return null;

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {crumbs.map((crumb, i) => (
        <span key={crumb.to} className="breadcrumb-item">
          {i > 0 && <ChevronRight size={14} className="breadcrumb-sep" />}
          {i === crumbs.length - 1 ? (
            <span aria-current="page">{crumb.label}</span>
          ) : (
            <Link to={crumb.to}>{crumb.label}</Link>
          )}
        </span>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
