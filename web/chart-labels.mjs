/** Screen-space label placement only. Never changes projected source coordinates. */
export function boxesOverlap(a, b) {
  return a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
}

export function boxTouchesCircle(box, circle) {
  const nearestX = Math.max(box.x, Math.min(circle.x, box.x + box.width));
  const nearestY = Math.max(box.y, Math.min(circle.y, box.y + box.height));
  return (nearestX - circle.x) ** 2 + (nearestY - circle.y) ** 2 <= circle.radius ** 2;
}

/** Try a bounded set of nearby positions. Omit the label if none fits safely. */
export function placeChartLabel({ anchor, width, height, bounds, circles, labels, inset = 12, gap = 8 }) {
  const candidates = [];
  for (const extra of [0, 14, 28]) {
    const reach = anchor.radius + gap + extra;
    candidates.push(
      { x: anchor.x + reach, y: anchor.y - height / 2 },
      { x: anchor.x - reach - width, y: anchor.y - height / 2 },
      { x: anchor.x - width / 2, y: anchor.y - reach - height },
      { x: anchor.x - width / 2, y: anchor.y + reach },
      { x: anchor.x + reach, y: anchor.y - reach - height },
      { x: anchor.x - reach - width, y: anchor.y - reach - height },
      { x: anchor.x + reach, y: anchor.y + reach },
      { x: anchor.x - reach - width, y: anchor.y + reach },
    );
  }
  for (const candidate of candidates) {
    const box = { ...candidate, width, height };
    if (box.x < inset || box.y < inset || box.x + width > bounds.width - inset || box.y + height > bounds.height - inset) continue;
    // Reserve each marker's complete bounding square, including its halo/tap area.
    if (circles.some(circle => boxesOverlap(box, { x: circle.x - circle.radius, y: circle.y - circle.radius, width: 2 * circle.radius, height: 2 * circle.radius })) || labels.some(label => boxesOverlap(box, label))) continue;
    return box;
  }
  return null;
}
