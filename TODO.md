## To Do List
### Higher Priorities
    

- [X] Design a main program to allow more fluid command line interaction.
  - [X] In progress. Create a map of calls with explicit functions.  
  

- [ ] Design UI for limited backend management (e.g., roi name maps)  
  - [X] Need to completely rewrite roi_name_manager.py
  - [ ] Use new best guess function in UI design


- [ ] Adapt code and validate for other treatment planning systems
   - [ ] Monaco
   - [ ] iPlan
   - [ ] Protons
   - [ ] Oncentra Brachytherapy
   - [ ] Outside validation

### Lower Priorities
- [ ] Add an import log

- [ ] Include a column in Plans for staging and a way to update it post-import


- [X] Add ability to plot a temporary plan not in the SQL DB
    - [ ] Design new app for plan review  
    

- [ ] Validate dicompyler-core DVH calculations

- [ ] Validate EUD calculations  
  
  
- [ ] Write DICOM pre-import validation function
    - [X] include similarity check with fuzzy wuzzy


- [ ] Add thorough comments throughout all code

- [ ] Incorporate BED, TCP, NTCP calculations

- [ ] Track wedge info on 3D beams  

- [ ] Clean text representation in date fields  

- [ ] Combine data and stats into one ColumnDataSource so endpoints are calculated for stats
