export interface MultiSelectProps {
    id: string;
    title: string;
    name: string;
    value: Array<string>;
    options: Array<string | [string, string]>;
}
declare var _default: (props: MultiSelectProps) => HTMLElement;
export default _default;
