export interface ToolbarProps {
    location: "above" | "below" | "left" | "right";
    sticky: "sticky" | "non-sticky";
    logo?: "normal" | "grey";
}
declare var _default: (props: ToolbarProps) => HTMLElement;
export default _default;
