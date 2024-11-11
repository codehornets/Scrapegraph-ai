# [Content Quality Service Spellcheck]

![Build](https://github.com/pfizer/stratus-core-ml/workflows/Python%20ML%20Build%20&%20Test/badge.svg)

### Before Writing _Any_ Code:

- https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/signing-commits

> NOTE you need docker locally to run the worker!

## Overview

Once you are ready to deploy just create a PR, watch it succeed then merge into Mainline. 

Make sure to keep the `requirements.txt` and `requirements-dev.txt` file up to date as needed.

* "requirements": Packages required by your application in production.
* "requirements-dev": Packages that are only needed for local development and testing.

## Installation

0. Install Python 3.7 and Docker
1. Clone the repo `git clone https://github.com/pfizer/[REPO_NAME]`
2. `cd` into the cloned folder
3. Create a virtual environment: `python3 -m virtualenv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Copy the environment file to your local `cp .env.example .env`
6. Install requirements `make install-dev`
8. Confirm tests work with `make test`
## Testing

Utilise your IDE's debugger as often as possible. There is tons of information on the internet for how to install and use debuggers. VSCode has a brilliant Python debugger which you should be using all the time.

Write tests as you write your code. As we can't (yet) reliably and quickly mock AWS resources locally, all functionality needs to be unit tested to a point where you are fully confident it will work once it's been deployed.

### References
* [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)

## Makefile

If you find yourself writing the same command over and over again, consider putting it into the [Makefile](Makefile). Docker commands can be especially long!

Try to describe the target with meaningful comments. They are parsed when running `make` or `make help` and printed near the target.

An example command would be:

```makefile
# Install "requirements.txt"
install:
	pip3 install -r requirements.txt
```

## Disclaimer

In order to create a form you should comply with all Pfizer data collection and retention policies as well any applicable laws and regulations regarding data collection and retention policies
Please refer to Corporate Policy # 403 – Acceptable Use of Information Systems.

2.3 ENTERPRISE RECORDS RETENTION SCHEDULE
The Pfizer Enterprise Records Retention Schedule (ERRS) defines the length of time a Company
Record must be retained based on legal and regulatory requirements.
You must adhere to the ERRS – along with Hold Notices – for all Company Records, regardless of the format of the records or the media on which they are stored.

Countries not listed within the scope of the ERRS may have differing laws and expectations
regarding the retention of Company Records. Consult local legal counsel regarding document
types and potential conflicting retention times that exceed stated ERRS retention.
You can find these requirements along with instructions on how to use the ERRS at
http://recordretention.pfizer.com.

2.7 PREFERRED FORMAT FOR RETAINING COMPANY RECORDS
Company Records should be retained in electronic, not physical, format unless Physical Company
Records are required specifically by law or regulation. Consult with local counsel to determine if
Physical Company Records must be maintained. In certain circumstances it may not be possible
or an appropriate business investment to convert Physical Company Records to electronic format.
Contact the eRIM organization at recordsmanagement@pfizer.com for further guidance

* REFERENCES:
Corporate Policy # 403 – Acceptable Use of Information Systems

* How to Archive Electronic Records

* eRIM website http://erim.pfizer.com

* ERRS website http://recordretention.pfizer.com/

* Hold Notices http://erim.pfizer.com

----  Data like Store Personal Health Information (PHI), health records, Personal Identifiable Information (PII) should not be stored within the microservice or passed into an email but should follow Pfizer policy on how to handle such data. -----
