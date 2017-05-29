export declare function register_event_class(event_name: string): (event_cls: typeof BokehEvent) => void;
export declare function register_with_event(event_cls: typeof BokehEvent, ...models: any[]): void;
export declare abstract class BokehEvent {
    event_name: string;
    applicable_models: any[];
    protected _options: any;
    model_id: string;
    constructor(options?: any);
    set_model_id(id: string): this;
    is_applicable_to(obj: any): boolean;
    static event_class(e: any): any;
    toJSON(): object;
    _customize_event(model: any): this;
}
export declare class ButtonClick extends BokehEvent {
}
export declare abstract class UIEvent extends BokehEvent {
}
export declare class LODStart extends UIEvent {
}
export declare class LODEnd extends UIEvent {
}
export declare class PointEvent extends UIEvent {
    sx: number;
    sy: number;
    x: number;
    y: number;
    constructor(options: any);
    static from_event(e: any, model_id?: string): PointEvent;
    _customize_event(plot: any): this;
}
export declare class Pan extends PointEvent {
    static from_event(e: any, model_id?: string): Pan;
    delta_x: number;
    delta_y: number;
    constructor(options?: any);
}
export declare class Pinch extends PointEvent {
    static from_event(e: any, model_id?: string): Pinch;
    scale: number;
    constructor(options?: any);
}
export declare class MouseWheel extends PointEvent {
    static from_event(e: any, model_id?: string): MouseWheel;
    delta: number;
    constructor(options?: any);
}
export declare class MouseMove extends PointEvent {
}
export declare class MouseEnter extends PointEvent {
}
export declare class MouseLeave extends PointEvent {
}
export declare class Tap extends PointEvent {
}
export declare class DoubleTap extends PointEvent {
}
export declare class Press extends PointEvent {
}
export declare class PanStart extends PointEvent {
}
export declare class PanEnd extends PointEvent {
}
export declare class PinchStart extends PointEvent {
}
export declare class PinchEnd extends PointEvent {
}
