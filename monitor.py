import requests
import argparse
import time
import logging
import sys
import os

class Monitor:
    """
    A class used to represent a monitoring service
    ...

    Attributes
    ----------
    email : str
        the email address to use when emailing support
    api_url : str
        the endpoint of the API to monitor
    num_attempts : int
        the number of retry attempts on an endpoint before emailing support
    sleep_time : int
        the time to sleep between requests to the endpoint in seconds

    Methods
    -------
    monitor()
        Begins the monitor process on the endpoint specified.
    postEmail()
        Sends an email to the specified email address
    """

    def __init__(self, email, api_url, num_attempts, sleep_time):
        """
        Parameters
        ----------
        email : str
            the email address to email
        api_url : str
            the endpoint to monitor
        num_attempts : int
            the number of retry attempts on an endpoint before emailing support
        sleep_time : int
            the time to sleep between requests to the endpoint in seconds
        """

        self.email = email
        self.api_url = api_url
        self.num_attempts = int(num_attempts)
        self.sleep_time = int(sleep_time)
        self._logger = logging.getLogger()
    
    def monitor(self):
        """Monitors the specified endpoint and emails a specified address
        if the endpoint is down for multiple request periods.

        Raises
        ------
        NotImplementedError
            If no url is specified to monitor.
        """

        if self.api_url is None:
            raise NotImplementedError("Unable to monitor an endpoint if no url is provided.")

        err_count = 0
        err_alert = False
        good_count = 0

        # begin monitor process
        while True:
            self._logger.info("Checking Health API!")

            # instantiate request to health api
            resp = requests.get(self.api_url)

            # retrieve and parse status code and msg
            cur_status_code = resp.status_code
            cur_status_msg = resp.json().get('status')

            # if the status code or msg are not 'OK', then begin counting retry attempts
            if cur_status_code != 200 or cur_status_msg != "OK":
                err_count += 1
                self._logger.warning("Health API is not OK. {} attempts.".format(err_count))
                
                # if retry attempts exceed number of attempts specified, email support
                # with the failure notice
                if err_count == self.num_attempts:
                    self._logger.error("Health API not OK. Alerting support.")
                    err_alert = True
                    self.postEmail({'status': cur_status_code, 'message': {'message': 
                        'The endpoint has currently failed {} times.'.format(err_count)}})

            # otherwise, if the api recovers within the sleep window, notify support
            # with the recovery notice
            if err_alert and (cur_status_code == 200 and cur_status_msg == "OK"):
                good_count += 1
                self._logger.warning("Health API is recovering. {} attempts.".format(good_count))
                if good_count == self.num_attempts:
                    err_alert = False
                    self._logger.error("Health API has recovered. Alerting support.")
                    self.postEmail({'status': cur_status_code, 'message': {'message': 
                        'The endpoint has recovered {} times.'.format(good_count)}})
                    good_count = 0
                    err_count = 0
            
            # do nothing if everything is ok
            if not err_alert and cur_status_code == 200 and cur_status_msg == "OK":
                err_count = 0
                err_alert = False
                self._logger.info("Health API has no issues.")

            time.sleep(self.sleep_time)

    def postEmail(self, content):
        """Emails the specified address with the current status and message

        Raises
        ------
        NotImplementedError
            If no email address is provided.
        """

        if self.email is None:
            raise NotImplementedError("Unable to email support if no email address is provided.")

        requests.post(
            os.environ.get('MAILGUN_API_DOMAIN'),
            auth=("api", os.environ.get('MAILGUN_API_KEY')),
            data={"from": "Excited User <erikpohleapps@gmail.com>",
                "to": 'erikpohleapps@gmail.com',
                "subject": content.get('status'),
                "text": content.get('message')})

        self._logger.info("Emailing support.")

if __name__ == '__main__':

    # instantiate the logger
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, 
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',)
    
    # instantiate the parser and get args from command line
    parser = argparse.ArgumentParser(description='a simple monitor service for a specified endpoint.')
    parser.add_argument('--support', help='the support group to email', default='support@garmin.com')
    parser.add_argument('--api', help='the api endpoint to monitor', default='https://api.qa.fitpay.ninja/health')
    parser.add_argument('--retry', help='the number of retry attempts before emailing', default=2)
    parser.add_argument('--sleep', help='the amount of time in seconds before retrying the endpoint', default=30)
    args = parser.parse_args()

    # create monitor class instance using health api endpoint
    health_monitor = Monitor(args.support, args.api, args.retry, args.sleep)

    # begin monitoring
    health_monitor.monitor()
    