import type { ViewBox } from "./models/ViewBox";

export function fitView(): ViewBox {
  return { x: 0, y: 0, width: 1250, height: 286 };
}

export function zoomView(
  view: ViewBox,
  factor: number,
  x: number,
  y: number,
): ViewBox {
  const scale = Math.max(0.35, Math.min(4, (1250 / view.width) * factor));
  const width = 1250 / scale;
  const height = 286 / scale;
  return {
    x: x - ((x - view.x) / view.width) * width,
    y: y - ((y - view.y) / view.height) * height,
    width,
    height,
  };
}
