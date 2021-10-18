from azure.data.tables import TableClient
from azure.data.tables import UpdateMode

class AzureTableHandler():

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.table_name = "datamatrixLastValue"
        self.partition_key = '1'
        self.row_key = '1'
        self.table_client = TableClient.from_connection_string(self.connection_string, table_name=self.table_name)

    def get_datamatrix_code(self):
        return self.table_client.get_entity(partition_key='1', row_key='1')['LastCode']

    def update_datamatrix_code(self, newvalue):
        entity = {
            "PartitionKey" : f"{self.partition_key}",
            "RowKey" : f"{self.row_key}",
            "LastCode" : f"{newvalue}"
        }
 
        self.table_client.update_entity(mode=UpdateMode.REPLACE, entity = entity)

if __name__ == "__main__":
    print('test?')
    tablehandler = AzureTableHandler()
    dmcode = tablehandler.get_datamatrix_code()
    print(dmcode)
    dmcode = int(dmcode)
    newcode = dmcode + 1
    newcode = f"{newcode:06d}"
    tablehandler.update_datamatrix_code(newcode)    
    print(tablehandler.get_datamatrix_code())