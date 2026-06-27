import * as THREE from "three";

export function circlePts(cx: number, cz: number, r: number) {
  const seg = Math.max(64, Math.ceil(2 * Math.PI * r * 6));
  return Array.from({ length: seg + 1 }, (_, i) => {
    const t = (i / seg) * 2 * Math.PI;
    return new THREE.Vector3(cx + r * Math.cos(t), 0.06, cz + r * Math.sin(t));
  });
}

export function ellipsePts(cx: number, cz: number, rx: number, rz: number) {
  const seg = Math.max(64, Math.ceil(2 * Math.PI * Math.max(rx, rz) * 6));
  return Array.from({ length: seg + 1 }, (_, i) => {
    const t = (i / seg) * 2 * Math.PI;
    return new THREE.Vector3(cx + rx * Math.cos(t), 0.06, cz + rz * Math.sin(t));
  });
}

export function planeRight(N: THREE.Vector3) {
  return new THREE.Vector3(N.z, 0, -N.x).normalize();
}

export function vCirclePts(center: THREE.Vector3, r: number, N: THREE.Vector3) {
  const right = planeRight(N);
  const seg = Math.max(64, Math.ceil(2 * Math.PI * r * 6));
  return Array.from({ length: seg + 1 }, (_, i) => {
    const t = (i / seg) * 2 * Math.PI;
    return new THREE.Vector3(
      center.x + r * Math.cos(t) * right.x,
      center.y + r * Math.sin(t),
      center.z + r * Math.cos(t) * right.z,
    );
  });
}

export function vEllipsePts(center: THREE.Vector3, rx: number, ry: number, N: THREE.Vector3) {
  const right = planeRight(N);
  const seg = Math.max(64, Math.ceil(2 * Math.PI * Math.max(rx, ry) * 6));
  return Array.from({ length: seg + 1 }, (_, i) => {
    const t = (i / seg) * 2 * Math.PI;
    return new THREE.Vector3(
      center.x + rx * Math.cos(t) * right.x,
      center.y + ry * Math.sin(t),
      center.z + rx * Math.cos(t) * right.z,
    );
  });
}
