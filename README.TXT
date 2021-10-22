PHYSEE SENSE Datamatrix Generator README

Table of Contents:
-PURPOSE AND WORKING PRINCIPLE
-OPERATION
-OUTPUT AND LOGGING
-TEMPLATE FILE RULES
-INSTALLATION
-CONFIGURATION
-DISCLAIMER

____________________________________
###PURPOSE AND WORKING PRINCIPLE###
____________________________________
The PHYSEE SENSE modules require unique Datamatrices on their exterior. The datamatrices are used to record the location of the module. This script generates an output file in vector format with unique datamatrices. Each datamatrix corresponds to a six digit code, for example "000123". The output file is used to laserprint the datamatrices onto the SENSE modules. 

To ensure a unique datamatrix, even in the event of a crash of this computer, the next code to be produced is stored on Azure Table Storage. If the program crashes during run time the uniqueness of later produced datamatrices should still be guaranteed. If Azure Table Storage crashes or is lost due to human error the last produced code can be retrieved from the logs or last produced output file. In that case Azure Table Storage should be reconfigured and updated with the next value.

The script takes in a template file (template.svg). All black squares in the template are replaced by a unique datamatrix of equal size. 
___________________________________
###OPERATION###
____________________________________
Operation is done manually though a command line interface, or automatically by double clicking a .bat file that runs the commands for you. 

--Operation through command line interface:
	1: Open the command prompt (windows key + R, then type cmd)

	Activate the virtual environment:
	1: Navigate to the location of this README file (run command cd [path to folder of README]
	2: Activate the virtual environment. Type venv\scripts\activate

	Run the program:
	1: Type python script.py --help for specific run instructions.

	The instructions will tell you how to do a TEST or PRODUCTION run, and how to send the output either to inkscape or directly to the printer.
	
--Operation through .bat file
	If installed correctly, a .bat or shortcut to a .bat file can be double clicked. This will automatically run the program using specific instructions.
	The .bat file should have a clear name that specifies how the program is run, for example Generate_Matrices_TEST_ToInkscape.bat
	
____________________________________
###OUTPUT AND LOGGING###
____________________________________
Output files are placed in directory /output_files with filename [date]-[time]_[MODE]_PHYSEE_SENSE_code_[first-code]_to_[last-code].svg

A rotating log with a maximum of 5 files with individual maximum filesize of 1mb is placed in /logs. The logs can be opened with any text editor. The logs will contain general information about each run as well as information about any crashes.
____________________________________
###TEMPLATE FILE RULES###
____________________________________
Template must be an .svg file
Template must be placed in same directory as script.py with name "template.svg"
All black squares (fill color #000000) will be replaced by data matrices.
The black squares must be of svg type <rect>
The length of the black squares should equal the width.
Any other elements will remain as-is

____________________________________
###INSTALLATION###
____________________________________
Installation is best done by a python developer.

Github repository: https://github.com/dbsmit/PHYSEE_Datamatrix_generator

1 Make sure to have python installed
2 Make a folder for the application and clone or copy the repository. If you have git installed in prompt:  git clone https://github.com/dbsmit/PHYSEE_Datamatrix_generator
3 Create a virtual environment (python3 -m venv [Path/to/application/folder]/venv
4 Install requirements using pip (pip install -r requirements.txt). Solve any issues.
5 Move on to configuration

____________________________________
###CONFIGURATION###
____________________________________
1 Make sure to have a storage account in an appropriately named resource group on Azure. 
2 Create a file called .env in the same directory as script.py
3 Copy the contents of template env into the .env file
4 Replace the appropriate values. You can find the Azure connection string in the Azure environment for the Physee Datamatrix Generator under keys
5 You can find a list of printers with command "wmic printer list brief" to find the PRINTER_NAME for the .env file
6 Create easy to use and appropriately named .bat files (and perhaps shortcuts) using the template bat. For example a file called Generate_Matrices_TEST_ToInkscape.bat that runs the command "script.py --test --target=toinkscape"


____________________________________
###DISCLAIMER###
____________________________________
Excelnerd.nl (kvk 69733317 registered in The Netherlands) is never responsible for any financial loss caused directly or indirectly by using this product. The terms and conditions of Excelnerd.nl are found at https://www.excelnerd.nl/Algemene-Voorwaarden_Excelnerd.pdf

