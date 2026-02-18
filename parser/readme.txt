structure

    1. __init__
        - define keyword

    2. init_parameter
        - initialize the source file, device and revision
        - merge the basic keyword and vendor's keyword
        - get the regmap and regpage
        - define the address range regarding the device

    3. start_parsing
        - parameters
            - dump : file name
            - device : device name
            - revision : revision number
            - ventor_keyword (bool) : option for adding vendor's keyword
        - method call
            --> init_parameter()
            --> step1_mathcing()
                - make "_parsing.txt" and "_parsing_adc.txt"
                - open the source file in binary mode
                    - check "SC_REL"
                    - check "LAST KMSG"
                    - check any keyword defined in init_parameter()
                    - "dump_register" : call step2_matching()
                    - "sc_charger_set_property" : call step3_mathcing()
                    - "sc_charger_check_dcmode_status" : call step4_matching()
                    - other cases : check the words in scan_list
        - make "process done" file
        - clear the parameters before exit the method