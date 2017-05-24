## To Do List
### Higher Priorities
    
- [ ] Design a setup.py (e.g, resolve sql_connect.cnf initialization)

- [X] Design test.py files

- [X] Design a main program to allow more fluid command line interaction.
  - [ ] In progress. Create a map of calls with explicit functions.

- [ ] Design UI for backend management

- [ ] Adapt code and validate for other treatment planning systems
   - [ ] Monaco
   - [ ] iPlan
   - [ ] Protons
   - [ ] Oncentra Brachytherapy
   - [ ] Outside validation

### Lower Priorities
- [X] Add ability to plot a temporary plan not in the SQL DB
    - [ ] Design new app for plan review

- [ ] Validate dicompyler-core DVH calculations

- [ ] Validate EUD calculations

- [ ] Write DICOM pre-import validation function

- [ ] Add thorough comments throughout all code

- [ ] Incorporate BED, TCP, NTCP calculations

- [ ] Track wedge info on 3D beams

- [X] Look into filtering by date range
    - [ ] Clean text representation in text field

- [ ] Combine data and stats into one ColumnDataSource so endpoints are calculated for stats
