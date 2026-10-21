// Preserve the approved face/hair/glasses; consume only the image-authored
// neck/shoulder extension. This is opacity compositing, not body deformation.
export function composeGrandmaShadow(original, extension) {
  const c = new OffscreenCanvas(original.width, original.height);
  const x = c.getContext('2d');
  const lower = new OffscreenCanvas(original.width, original.height);
  const lx = lower.getContext('2d');
  // Registration measured on the unchanged crown/profile, not eyeballed scale.
  lx.drawImage(extension, 0, 17);
  // The join lies inside the original opaque nape, so no semi-transparent
  // wedge, feathered anatomy, or hard seam is exposed.
  lx.clearRect(0, 0, lower.width, 740);
  lx.clearRect(0, 0, 400, 840);
  lx.globalCompositeOperation = 'source-in';
  lx.fillStyle = '#000';
  lx.fillRect(0, 0, lower.width, lower.height);
  x.drawImage(lower, 0, 0);
  x.drawImage(original, 0, 0);
  return c;
}
