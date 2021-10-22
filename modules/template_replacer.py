import pathlib
from modules import azure_table_handler, datamatrix_generator
from lxml import etree as ET
import win32api
import win32print
import time
import sys
from dotenv import find_dotenv, load_dotenv
import logging
import os

logger = logging.getLogger(__name__)

class PlaceDatamatricesInTemplate():
        
    def __init__(self, is_test):

        load_dotenv(find_dotenv())
        self.is_test = is_test
        self.mode = 'TEST' if self.is_test else 'PRODUCTION'
        self.printername = os.getenv("PRINTER_NAME")  #'Microsoft Print to PDF'
        self.inkscapepath = os.getenv("INKSCAPE_PATH")#r"C:\Program Files\Inkscape\bin\inkscape.exe"
        self.templatesvg = 'template.svg'
        self.connection_string = os.getenv("AZURE_TABLESTORAGE_CONNECTION_STRING")
        maindir = pathlib.Path(__file__).parent.parent.resolve()
        self.output_dir = maindir / 'output_files'
        self.dmcolor = '#000000'                #black

    def passed_prechecks(self, target):
        try:
            if self.connection_string == None:
                raise ValueError("Azure Table Storage connection string not set in environment variables.")
            if not os.path.isfile(self.templatesvg):
                raise FileExistsError(f'Template is not find in current directory. Please place template file in the same directory as script.py with name {self.templatesvg}')
            if target == 'toinkscape':
                if self.inkscapepath == None:
                    raise ValueError(f'INKSCAPE_PATH not set in environment variables. Please update the environment variables or .env file.')
                elif not os.path.isfile(self.inkscapepath):
                    raise FileExistsError(f'Inkscape is not found in location {self.inkscapepath}. Please update the environment variables or .env file.')
            if target == 'toprinter':
                if self.printername == None:
                    raise ValueError(f'PRINTER_NAME not set in environment variables. Please update the environment variables or .env file.')
                elif not self.printer_exists(self.printername): raise SystemError(f'Printer [{self.printername}] does not exist. Please update the environment variables or .env file.')

        except Exception as e:
            # logger.exception(e)
            logger.error(f'Prechecks not passed: {e}')
            return False
        return True
    
    def printer_exists(self, printername):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS + win32print.PRINTER_ENUM_LOCAL)
        for i in printers:
            if i[2] == printername: return True
        return False

    def azure_table_get_first_and_update(self, step):
        ath = azure_table_handler.AzureTableHandler(self.connection_string, self.mode)
        first_code = ath.get_datamatrix_code()
        self.last_code = int(first_code) + step - 1
        if self.last_code > 999999:
            raise(ValueError('All codes were used up. Last code of this file is more than 999999. '))
        next_code = f"{self.last_code + 1:06d}"
        ath.update_datamatrix_code(next_code)
        return first_code

    def get_rects(self, template_namespace):
        rects = []
        for rect in self.template_root.iter(f'{template_namespace}rect'):
                if rect.attrib['style'].find(f'fill:{self.dmcolor}') >= 0:
                
                    w = rect.attrib['width']
                    h = rect.attrib['height']
                         
                    if w != h:
                        raise ValueError(f'TEMPLATE ISSUE: The width does not equal the height of one of the replacement squares in the template (color {self.dmcolor}). Please fix this template issue.')
                    else:
                        rects.append(rect)

        if len(rects) < 1:
            raise ValueError(f'TEMPLATE ISSUE: 0 replacement squares with color {self.dmcolor} found in template file.')
        return rects

    def add_test_layer(self, template_namespace):
        g = ET.Element(f'{template_namespace}g')
        text = ET.SubElement(g, "text")
        text.set("style", "font-size:10.5833mm;line-height:1.25;font-family:sans-serif;word-spacing:0px;stroke-width:0.264583")
        text.set("x", "10")
        text.set("y", "20mm")
        text.text = "THIS FILE WAS PRODUCED IN TEST MODE. DO NOT USE THIS OUTPUT FOR PRODUCTION PURPOSES."

        for val in range(10, 100, 20):
            text = ET.SubElement(g, "text")
            text.set("style", "font-size:10.5833mm;line-height:1.25;font-family:sans-serif;word-spacing:0px;stroke-width:0.264583")
            text.set("x", f'{str(val)}mm')
            text.set("y", f'{str(val + 30)}mm')
            text.text = "TEST"
        self.template_root.append(g)

    def convert_template(self):
        template = self.templatesvg
        template_tree = ET.parse(template)
        self.template_root = template_tree.getroot()
        template_namespace = self.template_root.tag.replace("}svg", "}")

        try:
            rects = self.get_rects(template_namespace)
        except Exception as e:
            logger.error(e)
            sys.exit()

        num_replacements = len(rects)
        logging.info(f'Number of datamatrices to be generated: {num_replacements}')
        first = self.azure_table_get_first_and_update(num_replacements)
        DmGen = datamatrix_generator.DmGenerator(first, num_replacements, "#000000")

        if self.is_test: self.add_test_layer(template_namespace)
              
        for rect in rects:
            w = rect.attrib['width']
            x = rect.attrib['x']
            y = rect.attrib['y']
            matrix = DmGen.gen_datamatrix(w, x, y)
            parent = rect.getparent()
            path = ET.SubElement(parent, "path")
            
            for key in matrix:
                path.set(key, matrix[key])
            parent.replace(rect, path)
  
        self.output_file = f'{str(self.output_dir)}/{time.strftime("%Y%m%d-%H%M%S")}_{self.mode}_PHYSEE_SENSE_code_{first}_to_{self.last_code:06d}.svg'
        logging.info(f'Output file at location {self.output_file}')
        template_tree.write(self.output_file)

    def send_to_inkscape(self):
        win32api.ShellExecute(0, None, self.inkscapepath, self.output_file, ".", 0)

    def send_to_printer(self):
        try:
            win32api.ShellExecute (0, "print", self.output_file, self.printername, ".", 0)
        except Exception as e:
            logger.exception(e)
            logger.error(f'\n\nSend to printer did not succeed. To print manually, please open the output file in the following location: {self.output_file} \n\n')
