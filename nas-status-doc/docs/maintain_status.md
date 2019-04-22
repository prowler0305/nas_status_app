# Maintain NAS Platform and Application Status
SA3 Automation Core Team members can use the forms on this page to maintain the statuses displayed on the main page.

## Generate EmailsNotifications
Use the two forms to generate an email that will automatically include all the known email address registered. 

### Platform Outage
This form can be used to generate an email indicating that the NAS Platform will out of service and by association the application(s) that will be unavailable during that time.

After the email is sent, the Platform status is set to =="NOT ACTIVE"== which in turn overrides each applications separate status to =="NOT ACTIVE"== as well when displaying the status on the main page.

The **Outage End Date and time** will also be displayed on the main page as the **restored by** date and time.

### Send Email Notification
Use this form to write a free form email to be sent to users. The **From email address** will default to a @noreply.com address if left blank.

## Update NAS Platform and Application Status
This form allows for the toggling of the status for each individual application and the overall NAS Platform.

!!! note
    As indicated on the form, the status for the overall platform can only be toggled from =="NOT ACTIVE"== to =="ACTIVE"==. This is to ensure that the only way the status is being set to =="NOT ACTIVE"== is by sending out an Outage notification.