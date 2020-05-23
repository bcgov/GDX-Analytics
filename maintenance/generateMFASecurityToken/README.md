
# Generate MFA Security Token

The script contained in this folder is used to generate IAM Session Token from a base AWS profile and MFA code provided by the user as arguments. The session token is required in order to use AWS CLI or SAM CLI with MFA enabled IAM accounts. The Session Token is valid for 12 hours by default. The session token is saved into another profile hereafter denoted as \<mfa_profile\>.

## Prerequisites
* internet connection on localhost
* bash shell on localhost
* *curl* on localhost
* *AWS CLI* [installed](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) on localhost
* *mfa-serial* is added to each configured base profile from which you want to generate MFA token in file *~/.aws/config*. For example
  ```
  [default]
  ...
  mfa-serial = <default-mfa-serial>
  ...
  [profile non-prod]
  ...
  mfa-serial = <non-prod-mfa-serial>
  ``` 

  The value of *mfa-serial* can be obtained by going to your respective IAM account in web console > clicking *Security Credentials* tab > copying the string next to *Assigned MFA device* field.

## Usage
From bash shell,
```bash
curl -so- https://raw.githubusercontent.com/bcgov/GDX-Analytics/generateMFASecurityToken/maintenance/generateMFASecurityToken/generateMFASecurityToken.sh | bash -s -- [-m <mfa_profile>] <base_profile> <token>
```
where 
* option *[-m \<mfa_profile\>]* is the mfa profile name to be created or updated. Default to *mfa*.
* *\<base_profile\>* is the base profile name used to call STS service which contains AccessKey, SecretAccessKey of the IAM user
* *\<token\>* is the MFA token code read from your MFA device

After execution, append *--profile \<mfa_profile\>* to every AWS CLI or SAM CLI command issued before the session  token expires.

## Examples
* to create or update *mfa* profile based on *default* profile and MFA token code *12345*
  ```bash
  curl -so- https://raw.githubusercontent.com/bcgov/GDX-Analytics/generateMFASecurityToken/maintenance/generateMFASecurityToken/generateMFASecurityToken.sh | bash -s -- default 12345
  ```

* to create or update *non-prod-mfa* profile based on *non-prod* profile and MFA token code *54321*

  ```bash
  curl -so- https://raw.githubusercontent.com/bcgov/GDX-Analytics/generateMFASecurityToken/maintenance/generateMFASecurityToken/generateMFASecurityToken.sh | bash -s -- -m non-prod-mfa non-prod 54321
  ```

