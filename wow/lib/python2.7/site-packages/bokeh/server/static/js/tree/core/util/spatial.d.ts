export declare type Rect = {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
};
export declare abstract class SpatialIndex {
    abstract indices(rect: Rect): number[];
}
export declare class RBush extends SpatialIndex {
    private readonly index;
    constructor(points: (Rect & {
        i: number;
    })[]);
    readonly bbox: Rect;
    search(rect: Rect): (Rect & {
        i: number;
    })[];
    indices(rect: Rect): number[];
}
