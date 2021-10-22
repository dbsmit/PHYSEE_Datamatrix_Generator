from azure.data.tables import TableClient
from azure.data.tables import UpdateMode
from azure.core import MatchConditions
import logging
import sys

logger = logging.getLogger(__name__)
azureLogger = logging.getLogger('azure')
azureLogger.setLevel(logging.WARNING)

class AzureTableHandler():

    def __init__(self, connection_string, mode):

        self.connection_string = connection_string
        self.table_name = "datamatrixNextValue"
        self.partition_key = mode
        self.row_key = mode
        self.table_client = TableClient.from_connection_string(self.connection_string, table_name=self.table_name)


    def get_datamatrix_code(self):
        try:
            entity = self.table_client.get_entity(partition_key=self.partition_key, row_key=self.row_key)
            logger.info(f'Azure Table Service Entity Retrieved {entity}')
        except Exception as e:
            logging.exception(e)
            logging.error(f'{e} \n\n Something went wrong while trying to retrieve the last code from the Azure Table. Do you have internet? Has the Azure service been modified?')
            sys.exit()
        self.etag = entity._metadata["etag"]
        return entity['NextCode']

    def update_datamatrix_code(self, newvalue):
        entity = {
            "PartitionKey" : f"{self.partition_key}",
            "RowKey" : f"{self.row_key}",
            "NextCode" : f"{newvalue}"
        }
        try:
            result = self.table_client.update_entity(mode=UpdateMode.REPLACE, entity = entity, etag = self.etag, match_condition=MatchConditions.IfNotModified)
            result = logger.info(f'Azure Table Service Update to NextCode {newvalue} {result}')
            return result
        
        except Exception as e:
            logging.exception(e)
            logging.error(f'{e} \n\n Something went wrong while trying to update the Azure Table with a new value. Do you have internet? Has the Azure service been modified? If multiple machines are running this script there may have been a conflicting operation. In that case, try again.')
            sys.exit()

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