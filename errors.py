import config
import logging
from auth import switch_auth

#todo test handle error
def handle_error(status_code):
    if status_code in [420, 429, 503]:

        err_string = 'Twitter streaming: temporary error occured : ' + repr(status_code)
        print(err_string)
        logging.warning(err_string)


        switch_auth()
        return True


    elif status_code in [400, 401, 403, 404, 406, 410, 422, 500, 502, 504]:

        err_string = "Twitter streaming: error: " + repr(status_code)
        print(err_string)
        logging.warning(err_string)

        try:
            switch_auth()
            return False

        except Exception as e:

            err_string = "Could not recover from irremediable error "+str(status_code)+" :"+str(e)
            print(err_string)
            logging.critical(err_string)


        return False


    elif status_code in [200, 304]:

        print("Twitter streaming: " + status_code)
        #no need to log this

        return True

    else:

        err_string = "Received unknown status: " + repr(status_code)
        print(err_string)
        logging.critical(err_string)
        return False
