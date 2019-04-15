# Welcome to NAS Status Web Application Docs
The purpose of the NAS Status App is to provide a set of features for both the end users of the automation applications on the Network Automation Services Platform (NAS) and the SA3 Core Automation Team that maintains the applications, the project information for them, and it's deployment containers on the Openshift Platform.

This site is for the SA3 Core Automation Team and is meant as an internal documentation that covers the project layout, design, frameworks, and features of the application so that this application can be maintained and supported by any member of the SA3 Core Automation Team.

!!! warning
    This site talks about and documents the application url endpoints that are to be used only by SA3 Core Automation Team members. Sharing this documentation site with end users will expose functionality that could be triggered by them that could cause confusion in the end user community.

!!! summary 
    ### Nas Platform Status 
    https://nas-status.engapps.uscc.com
    
    This is the main page that displays the primary set of information that is useful for both end users and SA3 Automation
    Core team. Here you will find the overall status of the Platform and/or the individual applications status and other features for end users.
    
    The additional features on this page include the following:
        
    1. Ability to generate an email to the SA3 Automation Core Team with any questions.
    1. Links to the applications Sharepoint Project site maintained by the projects PM/PO's
    1. Link to the FAQs page where the user can find Frequent Asked Questions and the answers grouped by Application and a General category.
    1. Form to register an email address to send any notifications about the Nas Platform or specific applications to.
    1. An expandable List of registered emails
    1. Known Issues section to communicate with end users issues the SA3 Core team knows about, communicate workarounds, and possibly indicate when a fix might be on the way.
    
    ***
    ### Maintain NAS Status
    https://nas-status.engapps.uscc.com/nas/notify
    
    Provides features to generate notification emails to all registered users and maintain and update the status and additional status info display on the main page. See the [Maintain Status](maintain_status.md) page for more information.
    ***
    ### FAQs
    https://nas-status.engapps.uscc.com/nas/faqs
    
    Displays the Frequently Asked Questions and the Answers grouped by application name as well as a General category. This allows end users to do self service of their questions before emailing the SA3 Core Automation Team.
    ***
    ### Add FAQs
    https://nas-status.engapps.uscc.com/nas/add/faq
    
    Provides forms for the SA3 Automation Core Team to add, remove, maintain the FAQs displayed on the FAQs page. See the [Add FAQs](maintain_faqs.md) page for more information.

### Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
