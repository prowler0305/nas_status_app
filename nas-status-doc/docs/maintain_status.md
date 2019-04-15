# Maintain NAS Platform and Application Status
SA3 Automation Core Team members can use the forms on this page to maintain the statuses displayed on the main page.

## Outage Emails
The form can be used to generate an email indicating that the NAS Platform will out of service and by association the applications that will be unavailable during that time. The email is generated specifying the recievers are all the known registered emails to the application.

After the email is sent the Platform status is set to =="NOT ACTIVE"== which in turns overrides each applications separate status to =="NOT ACTIVE"== as well when displaying the status on the main page.

## Update NAS Platform and Application Status
This form allows for the toggling of the status for each individual application and the overall NAS Platform.

!!! note
    As indicated on the form, the status for the overall platform can only be toggled from =="NOT ACTIVE"== to =="ACTIVE". This is to ensure that the only way the status is being set to =="NOT ACTIVE" is by sending out an Outage notification.