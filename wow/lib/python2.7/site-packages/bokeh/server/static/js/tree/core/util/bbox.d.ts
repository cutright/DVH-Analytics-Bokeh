import { Rect } from "./spatial";
export declare function empty(): Rect;
export declare function positive_x(): Rect;
export declare function positive_y(): Rect;
export declare function union(a: Rect, b: Rect): Rect;
export interface IBBox {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
}
export declare class BBox implements IBBox {
    readonly x0: number;
    readonly y0: number;
    readonly x1: number;
    readonly y1: number;
    constructor(bbox?: IBBox);
    readonly minX: number;
    readonly minY: number;
    readonly maxX: number;
    readonly maxY: number;
    readonly pt0: [number, number];
    readonly pt1: [number, number];
    readonly x: number;
    readonly y: number;
    readonly width: number;
    readonly height: number;
    contains(x: number, y: number): boolean;
    union(that: IBBox): BBox;
}
