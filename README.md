# DevOps Garmin Take-Home Exercise

## About

I went with a very object heavy approach, where I created an object to assosciate with the monitor process. This was because I noticed that the code could be reused and be a lot more flexible if it worked with dynamic variables.

## Getting Started

Navigate to the root directory where monitor.py is located. The default parameters for running the program are shown below, if you wish to change anything just add a flag.

```
optional arguments:
  -h, --help         show this help message and exit
  --support SUPPORT  the support group to email
  --api API          the api endpoint to monitor
  --retry RETRY      the number of retry attempts before emailing
  --sleep SLEEP      the amount of time in seconds before retrying the endpoint
```

```python
python3 monitor.py --support somebody@garmin.com --api https://api.qa.fitpay.ninja/health --retry 2 --sleep 30
```

## Sample Endpoint for Testing

I developed a very simple REST API with Flask to use as a local endpoint for testing (sample_endpoint.py). It mocked the response that the Garmin Health API gave. I used it extensively to test my solution. In order to run the endpoint, use:

```python
flask --app sample_endpoint.py run
```