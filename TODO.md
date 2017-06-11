## To Do List
### Higher Priorities


- [ ] Add ability to plot two separate populations simultaneously

- [ ] Allow user to input list of MRNs to restrict population


- [ ] Adapt code and validate for other treatment planning systems
   - [X] Pinnacle >=9.0
   - [ ] Monaco
   - [ ] iPlan
   - [X] Raystation Protons
     - [ ] Add proton specific beam parameters
   - [ ] Oncentra Brachytherapy
   - [ ] Outside validation
   - [ ] Create separate import functions for each TPS  


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


- [ ] Track additional info from RTPLan
  - [ ] Wedge
  - [X] Support for rotating couch and collimator


- [ ] Clean text representation in date fields  

- [ ] Combine data and stats into one ColumnDataSource so endpoints are calculated for stats


- [ ] Adapt for python3
  - [X] print functions updated 



