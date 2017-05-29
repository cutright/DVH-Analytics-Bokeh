export declare function delay(func: () => void, wait: number): number;
export declare function defer(func: () => void): number;
export declare function throttle<T>(func: () => T, wait: number, options?: {
    leading?: boolean;
    trailing?: boolean;
}): () => T;
export declare function once<T>(func: () => T): () => T;
