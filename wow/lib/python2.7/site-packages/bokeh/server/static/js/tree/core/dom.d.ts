export declare type HTMLAttrs = {
    [name: string]: any;
};
export declare type HTMLChildren = Array<string | HTMLElement | Array<string | HTMLElement>>;
export declare function createElement(tag: string, attrs: HTMLAttrs, ...children: HTMLChildren): HTMLElement;
export declare const div: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, span: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, link: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, style: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, a: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, p: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, pre: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, input: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, label: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, canvas: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, ul: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, ol: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement, li: (attrs?: HTMLAttrs, ...children: (string | HTMLElement | (string | HTMLElement)[])[]) => HTMLElement;
export declare function show(element: HTMLElement): void;
export declare function hide(element: HTMLElement): void;
export declare function empty(element: HTMLElement): void;
export declare function position(element: HTMLElement): {
    top: number;
    left: number;
};
export declare function offset(element: HTMLElement): {
    top: number;
    left: number;
};
export declare function replaceWith(element: HTMLElement, replacement: HTMLElement): void;
