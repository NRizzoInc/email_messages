'use strict';
// This file contains all the button commands

import { parseForm/*, loadEmailDropdown*/ } from "./formProcessor.js"
import { loadResource, writeResizeTextarea, isVisible } from "./utils.js"
import { Dropdown } from "./dropdown.js"

const emailSelDropdown = new Dropdown("email-id-selector")
const urlsPath = "/static/urls.json"
// true means show (default everything to that except terminal data & selector)
const defaultDisplayDict = {
    "fname":        true,
    "lname":        true,
    "email":        true,
    "password":     true,
    "message":      true,
    "phone":        true,
    "carrier":      true,
    "textarea":     false,
    "selector":     false,
    "task":         null
}

$(document).ready( () => {
    // add event listener for each form button element
    const formBtnList = document.getElementsByClassName("myBtn")
    for (const btn of formBtnList) {
        btn.addEventListener("click", () => {
            onFormBtnClick(btn.id)
        })
    }

    // return button
    const returnBtn = document.getElementById("Go-Back-Btn")
    returnBtn.addEventListener("click", () => {
        exitForm()
    })

    const submitBtn = document.getElementById("Submit-Button")
    submitBtn.addEventListener("click", () => {
        // get the selected email id if receiving email
        const isReceiving = document.getElementById('Texting-Form').getAttribute("task") == "receiving"
        // only visible if currently selecting email from dropdown
        const isSelectingEmail = isVisible("email-id-selector")
        submitFormBtn(submitBtn, isReceiving, isSelectingEmail)
    })

    // prevent page from automatically returning to main page from form
    // goes back after form processing complete
    const formEl = document.getElementById("Texting-Form")
    formEl.addEventListener("submit", (event) => {
        event.preventDefault()
    }, true)
})

/**
 * @brief onClick callback for main page buttons that pulls up the new form page and hide buttons
 * @Note triggered by "Send", "Receive", and "Add Contact" buttons
 */
async function onFormBtnClick(id) {
    // manipulate form page based on which form is desired 
    document.getElementsByClassName('button-wrapper')[0].style.display = "none"
    document.getElementById('Texting-Form-Wrapper').style.display = "block"

    const displayDict = Object.assign({}, defaultDisplayDict) // deep copy
    // set name attributes to match task of button
    // make non-necessary form lines disappear
    if (id == 'text-receive-button') {
        displayDict.fname = false
        displayDict.lname = false
        displayDict.message = false
        displayDict.phone = false
        displayDict.carrier = false
        displayDict.task = "receiving"
        emailSelDropdown.clearDropdown()
    } 
    else if (id == 'text-send-button') {
        displayDict.phone = false
        displayDict.carrier = false
        displayDict.task = "sending"
    }
    else if (id == 'add-contact-button') {
        displayDict.message = false
        displayDict.password = false
        displayDict.task = "adding-contact"
    }
    else {
        console.error("ID Does Not Mean Anything");
    }
    setDisplays(displayDict)
}

/**
 * Helper function to set fields' visibility
 * @param {{
        "fname":        true,
        "lname":        true,
        "email":        true,
        "password":     true,
        "message":      true,
        "phone":        true,
        "carrier":      true,
        "textarea":     false,
        "selector":     false,
        "task":         null
    }} displayDict If a field is true, show it
 */
function setDisplays(displayDict) {
    const display = "flex"
    const hide    = "none"
    document.getElementById('firstname-container').style.display =          displayDict.fname     ? display : hide
    document.getElementById('lastname-container').style.display =           displayDict.lname     ? display : hide
    document.getElementById('email-container').style.display =              displayDict.email     ? display : hide
    document.getElementById('password-container').style.display =           displayDict.password  ? display : hide
    document.getElementById('message-container').style.display =            displayDict.message   ? display : hide
    document.getElementById('phone-number-container').style.display =       displayDict.phone     ? display : hide
    document.getElementById('carrier-container').style.display =            displayDict.carrier   ? display : hide
    document.getElementById('terminal-text-container').style.display =      displayDict.textarea  ? display : hide
    document.getElementById('email-id-selector').style.display =            displayDict.selector  ? display : hide

    // use name attribute in formProcessor to determine some actions
    document.getElementById('Texting-Form').setAttribute("task", displayDict.task)

    // remove any content stored within output textarea
    writeResizeTextarea("terminal-text", "")
}

/**
 * @brief onClick function for the form 'submit' button
 * @param {HTMLButtonElement} submitBtn The button element that was clicked (vanilla form)
 * @param {Boolean} isReceiving True if trying to receive emails
 * @param {Boolean} isSelectingEmail True if email dropdown is showing to allow user to pick email to fetch
 */
async function submitFormBtn(submitBtn, isReceiving, isSelectingEmail) {
    // has id of submit button (need to extrapolate form id parent)
    const triggerID = submitBtn.closest("form").id

    // get url to post to
    const urls = await loadResource(urlsPath)

    // skip form parsing if currently selecting email to fully fetch
    // this is true for sending & receiving (step #1 of "receiving")
    if (!isSelectingEmail) {
        let formAddr;
        if (triggerID.toLowerCase().includes("text")) {
            formAddr = urls.formSites.textForm
        } else if (triggerID.toLowerCase().includes("email")) {
            formAddr = urls.formSites.emailForm
        } else {
            console.error("Error: unknown triggerer case")
        }

        // receiving, but still need to select email id & show corresponding data in box (step #1)
        // hide everything besides dropdown menu & buttons
        // hide immediately or else there is a large delay in hidding it bc parse takes awhile
        if (isReceiving) {
            const displayDict = {}
            const currTask = document.getElementById('Texting-Form').getAttribute("task") // maintain state
            for (const key of Object.keys(defaultDisplayDict)) {
                displayDict[key] = key == "selector"
            }
            displayDict.task = currTask
            setDisplays(displayDict)
        }

        const resData = await parseForm(triggerID, formAddr)
        
        // fill dropdown so user can select which email to show
        if (isReceiving) parseEmailData(resData)
        // wait for another submit (after dropdown option is selected)
        // do not continue if default option is chosen (i.e. have not selected one)
        // this function will be called again and routed to case that does POST request
    } else if (isSelectingEmail && isReceiving) {
        // step #2 of receiving
        // case when need to do POST request to get backend to fully fetch selected email
        const dropdownData = emailSelDropdown.getData()
        const selEmailData = {
            emailId     : emailSelDropdown.getSelected().value,
            idDict      : dropdownData.idDict,
            emailList   : dropdownData.emailList,
            authKey     : dropdownData.authKey
        }

        // post collated data about selected email to allow backend to fully fetch
        const resDict = await postSelectedEmailData(selEmailData)

        // show textarea 
        const displayDict = {}
        const currTask = document.getElementById('Texting-Form').getAttribute("task") // maintain state
        for (const key of Object.keys(defaultDisplayDict)) {
            displayDict[key] = key == "selector" || key == "textarea"
        }
        displayDict.task = currTask
        setDisplays(displayDict)

        // write email in textarea
        writeResizeTextarea("terminal-text", resDict.emailContent)
    }
    
    if (!isReceiving) {
        // immediately go back if not receiving
        exitForm()
    }
}

/**
 * @brief Helper function that sends POST request containing information about the selected email
 * @param {{
 *   emailId: String,
 *   authKey: String,
 *   idDict: {'<email id>': {idx: '<list index>', desc: ''}, ...},
 *   emailList: [{To, From, DateTime, Subject, Body, idNum, unread}, ...],
 * }} data The data to post for backend to parse
 * @returns The POST request's response. What you really want is the "emailContent" field as it contains the full email
 */
async function postSelectedEmailData(data) {
    const urls = await loadResource(urlsPath)
    const emailDataPage = urls.infoSites.emailData
    const reqResponse = {}
    try {
        const resData = await $.ajax({
            url: emailDataPage,
            type: 'POST',
            // need both for flask to understand MIME Type
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(data),
        })
        Object.assign(reqResponse, reqResponse, resData) // merge dicts
    } catch (err) {
        console.log(`Failed to post to '${emailDataPage}': ${JSON.stringify(err)}`);
    }
    return reqResponse
}

/**
 * @brief Parse email data and add them to dropdown to allow ability to determine which email id to fully fetch
 * @param {{
 *   error: Boolean,
 *   text: String,
 *   authKey: String
 *   idDict: {'<email id>': {idx: '<list index>', desc: ''}, ...},
 *   emailList: [{To, From, DateTime, Subject, Body, idNum, unread}, ...]
 * }} emailData
 * If error, 'error' key will be true & message will be in 'text' key
 * "emailList": list of dicts with email message data
 * "idDict": dict of email ids mapped to indexes of emailMsgLlist
 */ 
async function parseEmailData(emailData) {
    for (const [optToAddID, infoDict] of Object.entries(emailData.idDict)) {
        const realVal = infoDict.idx // values that map to actual indexes within another list
        const text = infoDict.desc
        emailSelDropdown.addOption(realVal, text)
    }

    // need to store authKey, emailList, and other important info related to email dropdown
    emailSelDropdown.appendData(emailData)
}

/**
 * @brief Helper function that hides form and brings up the main page
 * @note Usually used by "Go Back" button
 */
function exitForm() {
    document.getElementsByClassName('button-wrapper')[0].style.display = "block"
    document.getElementById('Texting-Form-Wrapper').style.display = "none"
}
