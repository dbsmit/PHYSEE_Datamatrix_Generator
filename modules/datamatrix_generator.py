from ppf.datamatrix import DataMatrix
from IPython.display import SVG, display
from lxml import etree as ET
from lxml.etree import fromstring
import logging

logger = logging.getLogger(__name__)

class DmGenerator():

    def __init__(self, first_code, num_codes, fg):

        self.num_codes = num_codes
        self.fg = fg
        self.first_code = int(first_code)
        self.gen = self.gen_next()

    def gen_next(self):
        num = self.first_code
        codes_generated = 0
        while True:
            codes_generated += 1
            if codes_generated > self.num_codes: raise ValueError('CRITICAL: Somehow the script is trying to produce more datamatrices than were reserved in the Azure Table Service. To protect this service from generating duplicate codes the script has shut down.')
            yield num
            num += 1
           

    def gen_datamatrix(self, d, x , y):

        code = f"{next(self.gen):06d}"
        myDataMatrix = DataMatrix(code)

        parser = ET.XMLParser()
        dm_root = fromstring(myDataMatrix.svg(fg = self.fg).encode('utf-8'), parser=parser)
        dm_namespace = dm_root.tag.replace("}svg", "}")

        path = dm_root.find(f'{dm_namespace}path')
        pathstr = path.attrib['d']
        pathstr = pathstr.replace("M1,1.5", "M0, 0.5")
        
        path.set('d', pathstr)
        d = float(d)
        path.set('transform', f'matrix({d/10}, 0, 0, {d/10}, {x}, {y})')

        return path.attrib

if __name__ == "__main__":
    dm = DmGenerator("000001", 30, "#0000FF")
    print(dm.gen_datamatrix(50, 10, 20))
