from customtkinter import *
from CTkTable import CTkTable
import client
import chose_options as cho
import json

# CTk configs
window = CTk()

window.geometry("900x630")
window.resizable(False, False)
window.config(padx=20, pady=20)
window.title("HTTP client")

statusCode = StringVar()
responseHeaders = [["Key", "Value"]]

statusCode.set("Status: none")

headersSelectorDict = {}
headersResSize = 0

for header in cho.generalHeaders + cho.requestHeaders + cho.entityHeaders:
    headersSelectorDict[header] = False


# Handlers
def addBtnHandler():
    global headersResSize
    if headersKeySelector.get() == "":
        return

    # append to table
    headersReqTable.add_row(
        [headersKeySelector.get(), headerValues.get()], headersResSize + 1
    )

    # delete option
    headersSelectorDict[headersKeySelector.get()] = True

    values = [
        header for header in headersSelectorDict if headersSelectorDict[header] == False
    ]
    delValues = [
        header for header in headersSelectorDict if headersSelectorDict[header] == True
    ]
    # update options
    headersKeySelector.configure(values=values)
    headersKeySelector.set(values[0] if len(values) > 0 else "")
    headersRemoverKeySelector.configure(values=delValues)
    headersRemoverKeySelector.set(delValues[0])

    headersResSize += 1


def removeBtnHandler():
    if headersRemoverKeySelector.get() == "":
        return

    headersSelectorDict[headersRemoverKeySelector.get()] = False

    for i, header in enumerate(headersReqTable.values):
        if header[0] == headersRemoverKeySelector.get():
            headersReqTable.delete_row(i)
            break

    values = [
        header for header in headersSelectorDict if headersSelectorDict[header] == False
    ]
    delValues = [
        header for header in headersSelectorDict if headersSelectorDict[header] == True
    ]
    # update options
    headersKeySelector.configure(values=values)
    headersKeySelector.set(values[0])
    headersRemoverKeySelector.configure(values=delValues)
    headersRemoverKeySelector.set(delValues[0] if len(delValues) > 0 else "")


def sendBtnHandler():
    global responseHeaders

    headers = [
        (row[0], row[1]) for row in headersReqTable.values[1:]
    ]  # Skip the header row
    response = json.loads(
        client.request(
            methodMenu.get(), URL.get(), headers, bodyReqFrame.get(0.0, "end")
        )
    )

    status = response["status"]
    response_headers = response["headers"]
    body = response["body"]
    responseHeaders = [["Key", "Value"]] + [
        [key, value] for key, value in response_headers.items()
    ]

    print(f"[body] {body}")

    statusCode.set("Status: " + str(status))

    headersResTable.delete_rows([i for i in range(0, headersResTable.rows)])

    for header in responseHeaders:
        headersResTable.add_row(header, headersResTable.rows)

    bodyResFrame.delete(0.0, "end")
    bodyResFrame.insert(0.0, body)


# request section
methodMenu = CTkComboBox(window, values=cho.methods)
URL = CTkEntry(window, placeholder_text="URL", width=630, font=("", 11))
sendBtn = CTkButton(
    window, width=100, font=("", 11), text="Send", command=sendBtnHandler
)

requestDataFields = CTkTabview(window, width=870, height=200, anchor="nw")

headersReqTab = requestDataFields.add("Headers")
bodyReqTab = requestDataFields.add("Body")
headersReqFrame = CTkScrollableFrame(headersReqTab, width=830, height=190)
bodyReqFrame = CTkTextbox(bodyReqTab, width=850, height=210)
headersReqTable = CTkTable(
    headersReqFrame, column=2, values=[["Key", "Value"]], width=410
)

headersKeySelector = CTkOptionMenu(
    headersReqFrame,
    values=[
        header for header in headersSelectorDict if headersSelectorDict[header] == False
    ],
)
headerValues = CTkEntry(headersReqFrame, width=550)
addHeaderBtn = CTkButton(headersReqFrame, text="ADD", command=addBtnHandler)

headersRemoverKeySelector = CTkOptionMenu(
    headersReqFrame,
    values=[
        header for header in headersSelectorDict if headersSelectorDict[header] == True
    ],
)
removeHeaderBtn = CTkButton(headersReqFrame, text="Remove", command=removeBtnHandler)

headersRemoverKeySelector.set("")

methodMenu.grid(row=0, column=0)
URL.grid(row=0, column=1)
sendBtn.grid(row=0, column=2)
requestDataFields.grid(row=1, column=0, columnspan=3)

headersReqFrame.pack(fill="both", expand=True)
bodyReqFrame.pack(fill="both", expand=True)
headersReqTable.grid(row=0, column=0, columnspan=3, pady=(0, 10))

headersKeySelector.grid(row=1, column=0)
headerValues.grid(row=1, column=1)
addHeaderBtn.grid(row=1, column=2)

headersRemoverKeySelector.grid(row=2, column=0, pady=10)
removeHeaderBtn.grid(row=2, column=2, pady=10)

# response section

responseLabel = CTkLabel(window, text="Response", anchor="w")
statusCodeLabel = CTkLabel(window, textvariable=statusCode)

responseDataFields = CTkTabview(window, width=870, height=200, anchor="nw")

headersResTab = responseDataFields.add("Headers")
bodyResTab = responseDataFields.add("Body")
cookiesResTab = responseDataFields.add("Cookies")

headersResFrame = CTkScrollableFrame(headersResTab, width=830, height=200)
bodyResFrame = CTkTextbox(bodyResTab, width=850, height=210)
cookiesResFrame = CTkScrollableFrame(cookiesResTab, width=830, height=200)

headersResTable = CTkTable(headersResFrame, column=2, values=responseHeaders)
cookiesResTable = CTkTable(
    cookiesResFrame,
    column=7,
    values=[["Name", "Value", "Domain", "Path", "Expires", "HttpOnly", "Secure"]],
)

responseLabel.grid(row=2, column=0)
statusCodeLabel.grid(row=2, column=1, columnspan=2)

responseDataFields.grid(row=3, column=0, columnspan=3)

headersResFrame.pack(fill="both", expand=True)
bodyResFrame.pack(fill="both", expand=True)
cookiesResFrame.pack(fill="both", expand=True)

headersResTable.pack(fill="both", expand=True)
cookiesResTable.pack(fill="both", expand=True)

window.mainloop()
