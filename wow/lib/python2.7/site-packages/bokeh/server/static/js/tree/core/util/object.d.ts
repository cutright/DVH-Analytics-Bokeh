export declare const keys: (o: any) => string[];
export declare function values<T>(object: {
    [key: string]: T;
}): Array<T>;
export declare function extend<T, T1>(dest: T, source: T1): T & T1;
export declare function clone<T>(obj: T): T;
export declare function isEmpty<T>(obj: T): boolean;
