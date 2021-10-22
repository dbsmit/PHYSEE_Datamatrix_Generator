import sys, getopt
import logging
from logging.handlers import RotatingFileHandler
import os
from modules.template_replacer import PlaceDatamatricesInTemplate

logger = logging.getLogger(__name__)
log_dir = os.path.join(os.path.normpath(os.getcwd()), 'logs')
log_fname = os.path.join(log_dir, 'log')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(), RotatingFileHandler(log_fname, maxBytes = 1000000, backupCount=5)], level=logging.INFO)

def main(argv):
  
    logger.info('\n\n ### Script starts ### \n\n')
    help = """usage: python script.py [option][arg] \n
            Options and arguments: 

            --test          : Program runs as normal but retrieves codes from TEST database, not PRODUCTION.
                              Use to test functionality of this script and the template. 
                              Do not use output for production purposes.
            --target=[arg]  : Choose between "toinkscape" and "toprinter".
            --help          : View this message and exit.
            
            Example:
            The following command will run the script in test mode and open the output file in inkscape:
            python script.py --test --target=toinkscape

            Do not forget to activate the virtual environment first, otherwise you will have import errors. 
            
            For more information see README.txt
    """
    
    try:
        longopts, remainder = getopt.getopt(argv, "", ['test', 'target=', 'help'])
    except getopt.GetoptError as err:
        logger.error(err)
        print(help)
        sys.exit()

    is_test = False
    target = None
    for longopt, arg in longopts:
        if longopt == ('--test'):
            logger.info('\n\n### TEST mode is enabled. Last code will be retrieved from and updated to test key in azure, not production. DO NOT USE THIS OUTPUT FOR PRODUCTION PURPOSES. ### \n\n')
            is_test = True
        elif longopt == ('--target'):
            if arg == 'toinkscape' or arg == 'toprinter':
                target = arg
            else:
                logger.error('Argument for target not recognized. Script has not run.')
                print(help)
                sys.exit()
        elif longopt == ('--help'):
            print(help)
            sys.exit()               
        else:
            logger.error('Unhandled option or argument. Script has not run.')
            print(help)
            sys.exit()

    if target == None:
        logger.error('Target was not specified. Script has not run.')
        print(help)
        sys.exit()

    try:
        DmReplacer = PlaceDatamatricesInTemplate(is_test)
        if not DmReplacer.passed_prechecks(target): sys.exit()
        DmReplacer.convert_template()
        if target == 'toprinter': DmReplacer.send_to_printer()
        if target == 'toinkscape': DmReplacer.send_to_inkscape()

    except Exception as e:
        logger.exception("Unhandled exception")

    logger.info(f'\n\n ### Script ends ### \n\n')

if __name__ == "__main__":
   main(sys.argv[1:])