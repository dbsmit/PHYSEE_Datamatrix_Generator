#%%

#THE FOLLOWING HANDLER EXECUTES SOME BASIC TABLE ADMINISTRATION TASKS

from azure.data.tables import TableClient
from azure.data.tables import UpdateMode
from azure.storage.table import TableService, Entity
from azure.core import MatchConditions
import logging

class AzureTableHandler():

    def __init__(self):

        self.connection_string = 'DefaultEndpointsProtocol=https;AccountName=steuwsenseswwmatrixtool;AccountKey=kH+TLjWl3JOhiM+pAHOuRBfnn7Wj4I2xgBB9hwt132Jq+aRi8nm6J0R3DJTVnlR+d/3zH3xE0NZc+5Ge9VdLUQ==;EndpointSuffix=core.windows.net'
        self.table_name = "datamatrixNextValue"
        self.partition_key = 'TEST'
        self.row_key = 'TEST'
        self.table_service = TableService(connection_string = self.connection_string)
        # self.table_client = TableClient.from_connection_string(self.connection_string, table_name=self.table_name)




    def create_table(self):
        self.table_service.create_table(self.table_name)

    
    def insert_entity(self, key):
        entity = {
            "PartitionKey" : f"{key}",
            "RowKey" : f"{key}",
            "NextCode" : f"000000"
        }
        self.table_service.insert_entity(table_name = self.table_name, entity = entity)


    def get_datamatrix_code(self):
        entity = self.table_client.get_entity(partition_key=self.partition_key, row_key=self.row_key)
        self.etag = entity._metadata["etag"]
        
        return entity['NextCode']

    def update_datamatrix_code(self, newvalue):
        entity = {
            "PartitionKey" : f"{self.partition_key}",
            "RowKey" : f"{self.row_key}",
            "NextCode" : f"{newvalue}"
        }
 
        result = self.table_client.update_entity(mode=UpdateMode.REPLACE, entity = entity, etag = self.etag, match_condition=MatchConditions.IfNotModified)
        return(result)




#%%
# Insert OR UPDATENew datamatrix test code, the partition key set in the TH object (disabled to prevent accidental overrides)
TH = AzureTableHandler()
print(TH.get_datamatrix_code())
# print(str(TH.update_datamatrix_code('000000')))


#%%
#Create table (disabled to prevent accidental overwrites)
TH = AzureTableHandler()
# TH.create_table()

#%%
#Insert TEST and PRODUCTION keys
TH = AzureTableHandler()
# TH.insert_entity("TEST")
# TH.insert_entity("PRODUCTION")


# %%
from ppf.datamatrix import DataMatrix
from IPython.display import SVG, display

myDataMatrix = DataMatrix('Test!')
print(myDataMatrix.svg())
display(SVG(myDataMatrix.svg()))


filename = "result.svg"
f = open(filename, "w")
f.write(myDataMatrix.svg())
f.close()

# %%
from azure.data.tables import TableClient
from azure.data.tables import UpdateMode
from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError
import logging

class AzureTableHandler():

    def __init__(self, connection_string):

        self.connection_string = 'DefaultEndpointsProtocol=https;AccountName=datamatrixstorage;AccountKey=7Z6+Ox0FWQz/pAWPheLLUxpLI8ZLepMDb/rP8R4tD4FQD+Ie1mGz6nxtn+MoomJ1FnEXNjA+m3QI+GRv0ycZnA==;EndpointSuffix=core.windows.net'
        self.table_name = "datamatrixLastValue"
        self.partition_key = '1'
        self.row_key = '1'
        self.table_client = TableClient.from_connection_string(self.connection_string, table_name=self.table_name)


    def get_datamatrix_code(self):
        entity = self.table_client.get_entity(partition_key='1', row_key='1')
        self.etag = entity._metadata["etag"]
        print(entity)
        return entity['LastCode']

    def update_datamatrix_code(self, newvalue):
        entity = {
            "PartitionKey" : f"{self.partition_key}",
            "RowKey" : f"{self.row_key}",
            "LastCode" : f"{newvalue}"
        }

            result = self.table_client.update_entity(mode=UpdateMode.REPLACE, entity = entity, etag = self.etag, match_condition=MatchConditions.IfNotModified)

        print(result)
TH = AzureTableHandler()
print(TH.get_datamatrix_code)
print(TH.update_datamatrix_code(''))

#%%
from ppf.datamatrix import DataMatrix
from IPython.display import SVG, display
class DmGenerator():


    def __init__(self, first_code, num_codes, fg):

        self.num_codes = num_codes
        self.fg = fg
        self.first_code = int(first_code)
        self.gen = self.gen_next()

    def gen_next(self):
        num = self.first_code
        while True:
            yield num
            num += 1

    def gen_datamatrix(self, d, x , y):

        code = f"{next(self.gen):06d}"
        print(code)
        myDataMatrix = DataMatrix(code)

        parser = ET.XMLParser()
        dm_root = fromstring(myDataMatrix.svg(fg = self.fg).encode('utf-8'), parser=parser)
        dm_namespace = dm_root.tag.replace("}svg", "}")

        path = dm_root.find(f'{dm_namespace}path')
        pathstr = path.attrib['d']
        print(pathstr)
        pathstr = pathstr.replace("M1,1.5", "M0, 0.5")
        
        path.set('d', pathstr)
        d = float(d)
        path.set('transform', f'matrix({d/10}, 0, 0, {d/10}, {x}, {y})')


dm = DmGenerator("000001", 30, "#0000FF")
dm.gen_datamatrix(50, 10, 20)
dm.gen_datamatrix(50, 10, 20)
dm.gen_datamatrix(50, 10, 20)





#%%
import pysvg
# import xml.etree.ElementTree as ET
from lxml import etree as ET
from IPython.display import SVG, display
from lxml.etree import fromstring
import win32api

template = 'template_example.svg'
display(SVG(template))
# ET.register_namespace('', "http://www.w3.org/2000/svg")
template_tree = ET.parse(template)

template_root = template_tree.getroot()
output = 'output.svg'


template_namespace = template_root.tag.replace("}svg", "}")
g = ET.Element(f"{template_namespace}g")


first = "000001"
DmGen = DmGenerator(first, 30, "#0000FF")
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

template_tree.write(output)
display(SVG(output))
win32api.ShellExecute(0, None, r"C:\Program Files\Inkscape\bin\inkscape.exe", r'C:\Users\User\OneDrive\Documents\Excelnerd\PHYSEE\Datamatrix_generator\output.svg', ".", 0)



# %%
import win32api
import win32print

PRINTERNAME = '"Microsoft Print to PDF"'
win32api.ShellExecute (
    0,
    "print",
    filename,
    PRINTERNAME,
    ".",
    0
)







# %%
import wx
import win32api
import win32print
class ComboBoxFrame(wx.Frame):
    def __init__(self):
        # creates a drop down with the list of printers available
        wx.Frame.__init__(self, None, -1, 'Printers', size=(350, 300))
        panel = wx.Panel(self, -1)
        list=[]
        #Enum printers returns the list of printers available in the network
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_CONNECTIONS
            + win32print.PRINTER_ENUM_LOCAL)
        for i in printers:
            list.append(i[2])
        sampleList = list
        wx.StaticText(panel, -1, "Please select one printer from the list of printers to print:", (15, 15))
        self.combo =wx.ComboBox(panel, -1, "printers", (15, 40), wx.DefaultSize,sampleList, wx.CB_READONLY )
        btn2 = wx.Button(panel, label="Print", pos=(15, 60))
        btn2.Bind(wx.EVT_BUTTON, self.Onmsgbox)
        self.Centre()
        self.Show()

    def Onmsgbox(self, event):
        filename='result.svg'
        # here the user selected printer value will be given as input
        #print(win32print.GetDefaultPrinter ())

        print('"%s"' % self.combo.GetValue())
        win32api.ShellExecute (
          0,
          "print",
          filename,
          '"%s"' % self.combo.GetValue(),
          ".",
          0
        )
        print(self.combo.GetValue())


if __name__ =='__main__':
    app = wx.App()
    ComboBoxFrame().Show()
    app.MainLoop()


# %%
app = wx.App()
ComboBoxFrame().Show()
app.MainLoop()
# %%



#%%
from azure.data.tables import TableClient
from azure.data.tables import UpdateMode

# https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/samples/sample_update_upsert_merge_entities.py#L128-L129

connection_string = 'DefaultEndpointsProtocol=https;AccountName=datamatrixstorage;AccountKey=1Wbrptg1XUHsJppfxxt5kmOc9q9myB2vkC+KXTMoY4mh8/U4gEB+HdRgPvoYCYTbrr4kmcvm0w3c/1Zxdwawlw==;EndpointSuffix=core.windows.net'

table_name = "datamatrixLastValue"

with TableClient.from_connection_string(connection_string, table_name=table_name) as table:
    entities = list(table.list_entities())

    # get all entities
    for i, entity in enumerate(entities):
        print("Entity #{}: {}".format(entity, i))

    
    #get 1 entity
    got_entity = table.get_entity(partition_key='1', row_key='1')
    print("Received entity: {}".format(got_entity))

    #update entity:
    entity = {
        u"PartitionKey" : u"1",
        u"RowKey" : u"1",
        u"LastCode" : u"000003"
    }

    table.update_entity(mode=UpdateMode.REPLACE, entity = entity)

    got_entity = table.get_entity(partition_key='1', row_key='1')
    print("Received entity: {}".format(got_entity))

# %%
