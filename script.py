#2 objects: TableHandler, datamatrix Generator, 
import pathlib
from modules import azure_table_handler, datamatrix_generator
from lxml import etree as ET
from IPython.display import SVG, display
from lxml.etree import fromstring
import win32api
import time
import sys, getopt
from dotenv import find_dotenv, load_dotenv

import os


class PlaceDatamatricesInTemplate():
    
    def __init__(self):
        load_dotenv(find_dotenv())
        self.printername = os.getenv("PRINTER_NAME")  #'Microsoft Print to PDF'
        self.inkscapepath = os.getenv("INKSCAPE_PATH")#r"C:\Program Files\Inkscape\bin\inkscape.exe"
        self.templatesvg = 'template.svg'
        self.connection_string = os.getenv("AZURE_TABLESTORAGE_CONNECTION_STRING")
        maindir = pathlib.Path(__file__).parent.resolve()
        self.output_dir = maindir / 'output_files'


    def azure_table_get_first_and_update(self, step):
        ath = azure_table_handler.AzureTableHandler(self.connection_string)
        first_code = ath.get_datamatrix_code()
        self.last_code = int(first_code) + step
        next_code = f"{self.last_code + 1:06d}"
        ath.update_datamatrix_code(next_code)
        return first_code

    def convert_template(self):
        template = self.templatesvg
        display(SVG(template))
        # ET.register_namespace('', "http://www.w3.org/2000/svg")
        template_tree = ET.parse(template)

        template_root = template_tree.getroot()
        

        template_namespace = template_root.tag.replace("}svg", "}")
        g = ET.Element(f"{template_namespace}g")

        num_replacements = 30
        first = self.azure_table_get_first_and_update(num_replacements)
        DmGen = datamatrix_generator.DmGenerator(first, num_replacements, "#000000")
        # path = ET.Element("path")
        # ET.SubElement(g, "path")



        print(template_namespace)
        for rect in template_root.iter(f"{template_namespace}rect"):
            print(rect.tag)
            print(rect.attrib)
            print(rect.attrib['style'])
            if rect.attrib['style'].find('fill:#000000') >= 0:
                print('REPLACE')
                w = rect.attrib['width']
                h = rect.attrib['height']
                x = rect.attrib['x']
                y = rect.attrib['y']

                matrix = DmGen.gen_datamatrix(w, x, y)
                parent = rect.getparent()
                path = ET.SubElement(parent, "path")
                
                for key in matrix:
                    path.set(key, matrix[key])
                parent.replace(rect, path)
                
                # rect.set('style', 'fill:#ffffff;stroke:#ffffff;stroke-width:0;fill-opacity:1')                    #make squares white instead of deleting

            

        template_root.append(g)
        # print(ET.tostring(template_root))


        # for child in template_root:
        #     print(child.tag, child.attrib)
        self.output_file = f'{str(self.output_dir)}/{time.strftime("%Y%m%d-%H%M%S")}_PHYSEE_SENSE_code_{first}_to_{self.last_code:06d}.svg'
        print(self.output_file)
        template_tree.write(self.output_file)
        display(SVG(self.output_file))

    def send_to_inkscape(self):
        win32api.ShellExecute(0, None, self.inkscapepath, self.output_file, ".", 0)

    def send_to_printer(self):
        win32api.ShellExecute (0, "print", self.output_file, self.printername, ".", 0)

def main(argv):
    help = 'script.py --toprinter --toinkscape'
    try:
        longopts = getopt.getopt(argv, shortopts="", longopts=['toprinter', 'toinkscape'])
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    DmReplacer = PlaceDatamatricesInTemplate()
    DmReplacer.convert_template()
    for longopt in longopts[0]:
        print(longopt)
        if longopt == ('--toprinter', ''):
            print('toprinter')
            DmReplacer.send_to_printer()

        elif longopt == ('--toinkscape', ''):
            print('toinkscape')
            DmReplacer.send_to_inkscape()

if __name__ == "__main__":
   main(sys.argv[1:])