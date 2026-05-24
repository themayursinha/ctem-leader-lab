interface SkeletonProps {
  width?: string
  height?: string
  margin?: string
}

const Skeleton = ({ width = '100%', height = '1rem', margin = '0' }: SkeletonProps) => (
  <div className="skeleton" style={{ width, height, margin }} />
)

export default Skeleton
