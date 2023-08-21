export default function getConvexHull(points) {
  if (points.length <= 3) {
    return points; // If there are only 3 or fewer points, they are the convex hull
  }  

  // Find the point with the lowest y-coordinate (and leftmost if there's a tie)
  const minYPoint = points.reduce((min, point) => (point.lat < min.lat || (point.lat === min.lat && point.lng < min.lng)) ? point : min, points[0]);

  // Sort the points by polar angle from minYPoint
  const sortedPoints = points.slice().sort((a, b) => {
    const angleA = Math.atan2(a.lat - minYPoint.lat, a.lng - minYPoint.lng);
    const angleB = Math.atan2(b.lat - minYPoint.lat, b.lng - minYPoint.lng);
    return angleA - angleB;
  });


  const hull = [sortedPoints[0], sortedPoints[1]]; // Initialize convex hull with first two points

  // eslint-disable-next-line no-plusplus
  for (let i = 2; i < sortedPoints.length; i++) {
    while (hull.length > 1 && orientation(hull[hull.length - 2], hull[hull.length - 1], sortedPoints[i]) !== 2) {        
        hull.pop(); // Remove last point if it's not making a left turn
    }    
    hull.push(sortedPoints[i]); // Add the current point to the hull
  }
  
  hull.push(sortedPoints[0]); // Add the first point to the end of the hull to complete it
  return hull;
}

function orientation(p, q, r) {
  const val = (q.lng - p.lng) * (r.lat - q.lat) - (q.lat - p.lat) * (r.lng - q.lng);  
  if (val === 0) return 0; // Collinear
  return (val < 0) ? 1 : 2; // Clockwise or Counterclockwise
}
