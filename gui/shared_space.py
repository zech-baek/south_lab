class shared_class:
    
    def __init__(self):
        
        self.device    = None
        self.revision  = None
        self.emulator  = "cp2112" # default
        self.hidden    = False
        self.connect   = False
        self.debugging = True
        self.logging   = False
        self.height    = 600
        
        self.dict_layout  = dict() # refer to the gui/layout path
        self.dict_project = dict() # refer to the project path
        
        self.rw_interface = None
        self.temp = "debugging"
        
        # variables for main.py
        self.selected_tab = None
        self.list_tab  = list()
        self.reset_key = "reset_from_shortcut"
        
        # path
        self.root_dir    = None
        self.gui_dir     = None
        self.log_dir     = None
        self.project_dir = None
        self.layout_dir  = None
    

shared_var = shared_class()