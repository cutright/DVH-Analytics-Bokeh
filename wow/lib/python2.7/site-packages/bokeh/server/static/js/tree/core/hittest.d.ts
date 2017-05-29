export declare var point_in_poly: (x: any, y: any, px: any, py: any) => boolean;
export declare var HitTestResult: () => void;
export declare var create_hit_test_result: () => any;
export declare var create_1d_hit_test_result: (hits: any) => any;
export declare var validate_bbox_coords: (arg: any, arg1: any) => {
    minX: any;
    minY: any;
    maxX: any;
    maxY: any;
};
export declare var dist_2_pts: (vx: any, vy: any, wx: any, wy: any) => any;
export declare var dist_to_segment: (p: any, v: any, w: any) => number;
export declare var check_2_segments_intersect: (l0_x0: any, l0_y0: any, l0_x1: any, l0_y1: any, l1_x0: any, l1_y0: any, l1_x1: any, l1_y1: any) => {
    hit: boolean;
    x: any;
    y: any;
};
