export interface SelectProps {
    id: string;
    title: string;
    name: string;
    value: string;
    options: Array<string | [string, string]>;
}
declare var _default: (props: SelectProps) => HTMLElement;
export default _default;
