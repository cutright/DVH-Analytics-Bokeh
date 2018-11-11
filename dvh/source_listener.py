class SourceSelection:
    def __init__(self, table, sources, allow_source_update):
        self.table = table
        self.sources = sources
        self.allow_source_update = allow_source_update

    def ticker(self, attr, old, new):
        if self.allow_source_update:
            src = getattr(self.sources, self.table)
            uids = list(set([src.data['uid'][i] for i in new]))
            self.update_planning_data_selections(uids)

    def update_planning_data_selections(self, uids):

        self.allow_source_update = False
        for k in ['rxs', 'plans', 'beams']:
            src = getattr(self.sources, k)
            src.selected.indices = [i for i, j in enumerate(src.data['uid']) if j in uids]

        self.allow_source_update = True


class SourceListener:
    def __init__(self, sources, query, dvhs, rad_bio, regression):

        self.sources = sources
        self.query = query
        self.dvhs = dvhs
        self.rad_bio = rad_bio
        self.regression = regression

        self.sources.selectors.selected.on_change('indices', self.query.update_selector_row_on_selection)
        self.query.update_selector_source()

        self.sources.ranges.selected.on_change('indices', self.query.update_range_row_on_selection)
        self.sources.endpoint_defs.selected.on_change('indices', self.dvhs.update_ep_row_on_selection)

        tables = ['rxs', 'plans', 'beams']
        self.source_selection = {s: SourceSelection(s, self.sources, self.query.allow_source_update) for s in tables}
        for s in tables:
            getattr(self.sources, s).selected.on_change('indices', self.source_selection[s].ticker)
        self.sources.dvhs.selected.on_change('indices', self.dvhs.update_source_endpoint_view_selection)
        self.sources.endpoint_view.selected.on_change('indices', self.dvhs.update_dvh_table_selection)
        self.sources.emami.selected.on_change('indices', self.rad_bio.emami_selection)
        self.sources.multi_var_include.selected.on_change('indices', self.regression.multi_var_include_selection)
