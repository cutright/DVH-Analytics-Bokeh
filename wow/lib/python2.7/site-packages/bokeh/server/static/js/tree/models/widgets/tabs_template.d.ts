export interface TabsProps {
    tabs: Array<{
        id: string;
        title: string;
    }>;
    active_tab_id: string;
}
declare var _default: (props: TabsProps) => HTMLElement;
export default _default;
